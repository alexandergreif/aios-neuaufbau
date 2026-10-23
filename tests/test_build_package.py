import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / "scripts/build_package.py"
SCRIPT_NAMES = {"languages.py", "setup_profile.py", "profile_transfer.py", "check_config.py", "check_register.py",
                "setup_status.py", "safe_files.py", "package_rules.py", "package_inventory.py"}


class PackageBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=PACKAGE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.destination = self.root / "runtime"

    def run_cli(self, *args, answer=""):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], input=answer, capture_output=True, text=True)

    def load_builder(self):
        with patch.object(sys, "path", [str(PACKAGE / "scripts"), *sys.path]):
            spec = importlib.util.spec_from_file_location("build_package_test", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    def fake_package(self):
        fake = self.root / "fake-package"
        (fake / "de/regeln").mkdir(parents=True)
        (fake / "de/regeln/kern.md").write_text("# Kern\n", encoding="utf-8")
        (fake / "scripts").mkdir()
        for name in SCRIPT_NAMES:
            (fake / "scripts" / name).write_text("# synthetic\n", encoding="utf-8")
        return fake

    def test_preview_and_cancel_do_not_write(self):
        preview = self.run_cli("--destination", self.destination)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertFalse(self.destination.exists())
        cancel = self.run_cli("--destination", self.destination, "--apply", answer="no\n")
        self.assertEqual(cancel.returncode, 0, cancel.stderr)
        self.assertFalse(self.destination.exists())

    def test_package_is_self_contained_and_manifest_matches(self):
        result = self.run_cli("--destination", self.destination, "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = {p.relative_to(self.destination).as_posix() for p in self.destination.rglob("*") if p.is_file()}
        source_general = {"allgemein/" + p.relative_to(PACKAGE / "de").as_posix() for p in (PACKAGE / "de").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        expected = source_general | {f"scripts/{name}" for name in SCRIPT_NAMES} | {"AGENTS.md", "CLAUDE.md", "paket.json"}
        self.assertEqual(actual, expected)
        manifest = json.loads((self.destination / "paket.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["version"], "0.2.0-dev")
        self.assertEqual(manifest["language"], "de")
        self.assertEqual({entry["path"] for entry in manifest["files"]}, actual - {"paket.json"})
        for entry in manifest["files"]:
            self.assertEqual(entry["sha256"], hashlib.sha256((self.destination / entry["path"]).read_bytes()).hexdigest())
            self.assertFalse(Path(entry["path"]).is_absolute())
        generated = (self.destination / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(generated, (self.destination / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("(allgemein/referenzen/externes-schreiben.md)", generated)
        self.assertTrue(generated.startswith("<!-- Generiert aus allgemein/regeln/kern.md. SHA256: "))
        self.assertNotIn(str(PACKAGE), generated)
        for name in SCRIPT_NAMES:
            help_result = subprocess.run([sys.executable, str(self.destination / "scripts" / name), "--help"], capture_output=True, text=True)
            self.assertEqual(help_result.returncode, 0, f"{name}: {help_result.stderr}")

    def test_no_development_or_private_files(self):
        result = self.run_cli("--destination", self.destination, "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        names = {p.relative_to(self.destination).as_posix() for p in self.destination.rglob("*") if p.is_file()}
        self.assertNotIn("scripts/prepare_client.py", names)
        self.assertNotIn("scripts/check_client_loader.py", names)
        self.assertFalse(any(name.startswith("tests/") or name.startswith("docs/") or "__pycache__" in name for name in names))
        self.assertFalse(any(Path(name).name.startswith(".env") and Path(name).name != ".env.example" for name in names))
        self.assertFalse(any("profil.md" == Path(name).name and not name.startswith("allgemein/vorlagen/") for name in names))

    def test_existing_destination_remains_unchanged(self):
        self.destination.mkdir()
        marker = self.destination / "keep.txt"
        marker.write_text("keep", encoding="utf-8")
        result = self.run_cli("--destination", self.destination, "--apply", answer="yes\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
        self.assertEqual(list(self.destination.iterdir()), [marker])

    def test_nested_symlink_and_secret_are_rejected(self):
        builder = self.load_builder()
        fake = self.fake_package()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "marker.md").write_text("do not read", encoding="utf-8")
        (fake / "de/referenzen").symlink_to(outside, target_is_directory=True)
        with patch.object(builder, "PACKAGE", fake), patch.object(Path, "read_bytes", side_effect=AssertionError("outside read")):
            with self.assertRaises(builder.BuildError):
                builder.source_snapshot()
        (fake / "de/referenzen").unlink()
        (fake / "de/.env").write_text("SECRET=synthetic", encoding="utf-8")
        with patch.object(builder, "PACKAGE", fake):
            with self.assertRaises(builder.BuildError):
                builder.source_snapshot()

    def test_misplaced_private_runtime_data_rejected_before_read(self):
        builder = self.load_builder()
        fake = self.fake_package()
        misplaced = (
            "de/profil.md",
            "de/pfade.json",
            "de/projekte.md",
            "de/zustand/state.json",
            "de/wissen/INDEX.md",
            "de/vorlagen/wissen/private-note.md",
            "de/secrets/token.txt",
            "de/credentials/token.txt",
            "de/journals/action.json",
        )
        for name in misplaced:
            with self.subTest(name=name):
                path = fake / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("SYNTHETIC_PRIVATE_MARKER", encoding="utf-8")
                with patch.object(builder, "PACKAGE", fake), patch.object(builder, "read_relative", side_effect=AssertionError("content read")):
                    with self.assertRaises(builder.BuildError):
                        builder.source_snapshot()
                path.unlink()
                if name.split("/")[1] in ("zustand", "wissen", "secrets", "credentials", "journals"):
                    (fake / "de" / name.split("/")[1]).rmdir()
        (fake / "de/.env.example").write_text("PLACEHOLDER=\n", encoding="utf-8")
        with patch.object(builder, "PACKAGE", fake):
            self.assertIn(Path("allgemein/.env.example"), builder.source_snapshot())

    def test_transient_source_symlink_is_rejected(self):
        builder = self.load_builder()
        fake = self.fake_package()
        marker = self.root / "outside-marker.md"
        marker.write_text("FOREIGN_MARKER", encoding="utf-8")
        source = fake / "de/regeln/kern.md"
        parked = fake / "de/regeln/kern.parked"
        original_read = builder.read_relative

        def swap_during_read(package_fd, relative, expected):
            if relative != Path("de/regeln/kern.md"):
                return original_read(package_fd, relative, expected)
            source.rename(parked)
            source.symlink_to(marker)
            try:
                return original_read(package_fd, relative, expected)
            finally:
                source.unlink()
                parked.rename(source)

        with patch.object(builder, "PACKAGE", fake), patch.object(builder, "read_relative", side_effect=swap_during_read):
            with self.assertRaises(builder.BuildError):
                builder.source_snapshot()
        self.assertEqual(source.read_text(encoding="utf-8"), "# Kern\n")

    def test_source_change_after_preview_stops_build(self):
        builder = self.load_builder()
        fake = self.fake_package()

        def change_after_preview(_prompt):
            (fake / "de/regeln/kern.md").write_text("# Changed\n", encoding="utf-8")
            return "yes"

        with patch.object(builder, "PACKAGE", fake), patch("builtins.input", side_effect=change_after_preview):
            result = builder.main(["--destination", str(self.destination), "--apply"])
        self.assertEqual(result, 1)
        self.assertFalse(self.destination.exists())

    def fake_english_package(self):
        fake = self.fake_package()
        for relative, text in (("en/rules/core.md", "# Core\n\nSee [storage](../references/storage.md).\n"),
                               ("en/references/storage.md", "# Storage\n"),
                               ("en/skills/demo/SKILL.md", "---\nname: demo\ndescription: Demo.\n---\nBody\n"),
                               ("en/templates/profile.md", "# Personal profile\n"),
                               ("en/templates/knowledge/INDEX.md", "# Knowledge index\n"),
                               ("en/templates/project/NOTES.md", "# Project notes\n"),
                               ("en/configuration/paths.template.json", "{}\n"),
                               ("en/configuration/.env.example", "BLOCKBRAIN_API_KEY=\n")):
            path = fake / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return fake

    def test_english_package_uses_general_root_and_records_language(self):
        builder = self.load_builder()
        fake = self.fake_english_package()
        with patch.object(builder, "PACKAGE", fake), patch("builtins.input", return_value="yes"):
            self.assertEqual(builder.main(["--destination", str(self.destination), "--language", "en", "--apply"]), 0)
        actual = {p.relative_to(self.destination).as_posix() for p in self.destination.rglob("*") if p.is_file()}
        self.assertIn("general/rules/core.md", actual)
        self.assertIn("general/skills/demo/SKILL.md", actual)
        self.assertIn("general/templates/knowledge/INDEX.md", actual)
        self.assertIn("general/configuration/.env.example", actual)
        self.assertFalse(any(name.startswith(("allgemein/", "de/", "en/")) for name in actual))
        manifest = json.loads((self.destination / "paket.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["language"], "en")
        self.assertEqual(manifest["version"], "0.2.0-dev")
        generated = (self.destination / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(generated.startswith("<!-- Generated from general/rules/core.md. SHA256: "))
        self.assertIn("(general/references/storage.md)", generated)

    def test_english_private_files_rejected_before_read(self):
        builder = self.load_builder()
        fake = self.fake_english_package()
        for name in ("en/profile.md", "en/paths.json", "en/projects.md", "en/state/x.json",
                     "en/knowledge/INDEX.md", "en/templates/knowledge/private-note.md"):
            with self.subTest(name=name):
                path = fake / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("SYNTHETIC_PRIVATE_MARKER", encoding="utf-8")
                with patch.object(builder, "PACKAGE", fake), patch.object(builder, "read_relative", side_effect=AssertionError("content read")):
                    with self.assertRaises(builder.BuildError):
                        builder.source_snapshot("en")
                path.unlink()
                if name.split("/")[1] in ("state", "knowledge"):
                    path.parent.rmdir()


if __name__ == "__main__":
    unittest.main()
