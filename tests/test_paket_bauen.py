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
SCRIPT = PACKAGE / "scripts/paket_bauen.py"
SCRIPT_NAMES = {"einrichten.py", "profil_transfer.py", "pruefe_konfiguration.py", "pruefe_register.py",
                "einrichtungsstatus.py", "sichere_dateien.py", "paketregeln.py", "paketbestand.py"}


class PackageBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=PACKAGE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.destination = self.root / "runtime"

    def run_cli(self, *args, answer=""):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], input=answer, capture_output=True, text=True)

    def load_builder(self):
        with patch.object(sys, "path", [str(PACKAGE / "scripts"), *sys.path]):
            spec = importlib.util.spec_from_file_location("paket_bauen_test", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    def fake_package(self):
        fake = self.root / "fake-package"
        (fake / "allgemein/regeln").mkdir(parents=True)
        (fake / "allgemein/regeln/kern.md").write_text("# Kern\n", encoding="utf-8")
        (fake / "scripts").mkdir()
        for name in SCRIPT_NAMES:
            (fake / "scripts" / name).write_text("# synthetic\n", encoding="utf-8")
        return fake

    def test_preview_and_cancel_do_not_write(self):
        preview = self.run_cli("--destination", self.destination)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertFalse(self.destination.exists())
        cancel = self.run_cli("--destination", self.destination, "--apply", answer="nein\n")
        self.assertEqual(cancel.returncode, 0, cancel.stderr)
        self.assertFalse(self.destination.exists())

    def test_package_is_self_contained_and_manifest_matches(self):
        result = self.run_cli("--destination", self.destination, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = {p.relative_to(self.destination).as_posix() for p in self.destination.rglob("*") if p.is_file()}
        source_general = {p.relative_to(PACKAGE).as_posix() for p in (PACKAGE / "allgemein").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        expected = source_general | {f"scripts/{name}" for name in SCRIPT_NAMES} | {"AGENTS.md", "CLAUDE.md", "paket.json"}
        self.assertEqual(actual, expected)
        manifest = json.loads((self.destination / "paket.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["version"], "0.1.0-dev")
        self.assertEqual({entry["path"] for entry in manifest["files"]}, actual - {"paket.json"})
        for entry in manifest["files"]:
            self.assertEqual(entry["sha256"], hashlib.sha256((self.destination / entry["path"]).read_bytes()).hexdigest())
            self.assertFalse(Path(entry["path"]).is_absolute())
        generated = (self.destination / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(generated, (self.destination / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("(allgemein/referenzen/externes-schreiben.md)", generated)
        self.assertNotIn(str(PACKAGE), generated)
        for name in SCRIPT_NAMES:
            help_result = subprocess.run([sys.executable, str(self.destination / "scripts" / name), "--help"], capture_output=True, text=True)
            self.assertEqual(help_result.returncode, 0, f"{name}: {help_result.stderr}")

    def test_no_development_or_private_files(self):
        result = self.run_cli("--destination", self.destination, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        names = {p.relative_to(self.destination).as_posix() for p in self.destination.rglob("*") if p.is_file()}
        self.assertNotIn("scripts/client_vorbereiten.py", names)
        self.assertNotIn("scripts/pruefe_client_loader.py", names)
        self.assertFalse(any(name.startswith("tests/") or name.startswith("docs/") or "__pycache__" in name for name in names))
        self.assertFalse(any(Path(name).name.startswith(".env") and Path(name).name != ".env.example" for name in names))
        self.assertFalse(any("profil.md" == Path(name).name and not name.startswith("allgemein/vorlagen/") for name in names))

    def test_existing_destination_remains_unchanged(self):
        self.destination.mkdir()
        marker = self.destination / "keep.txt"
        marker.write_text("keep", encoding="utf-8")
        result = self.run_cli("--destination", self.destination, "--apply", answer="ja\n")
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
        (fake / "allgemein/referenzen").symlink_to(outside, target_is_directory=True)
        with patch.object(builder, "PACKAGE", fake), patch.object(Path, "read_bytes", side_effect=AssertionError("outside read")):
            with self.assertRaises(builder.BuildError):
                builder.source_snapshot()
        (fake / "allgemein/referenzen").unlink()
        (fake / "allgemein/.env").write_text("SECRET=synthetic", encoding="utf-8")
        with patch.object(builder, "PACKAGE", fake):
            with self.assertRaises(builder.BuildError):
                builder.source_snapshot()

    def test_misplaced_private_runtime_data_rejected_before_read(self):
        builder = self.load_builder()
        fake = self.fake_package()
        misplaced = (
            "allgemein/profil.md",
            "allgemein/pfade.json",
            "allgemein/projekte.md",
            "allgemein/zustand/state.json",
            "allgemein/wissen/INDEX.md",
            "allgemein/vorlagen/wissen/private-note.md",
            "allgemein/secrets/token.txt",
            "allgemein/credentials/token.txt",
            "allgemein/journals/action.json",
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
                    (fake / "allgemein" / name.split("/")[1]).rmdir()
        (fake / "allgemein/.env.example").write_text("PLACEHOLDER=\n", encoding="utf-8")
        with patch.object(builder, "PACKAGE", fake):
            self.assertIn(Path("allgemein/.env.example"), builder.source_snapshot())

    def test_transient_source_symlink_is_rejected(self):
        builder = self.load_builder()
        fake = self.fake_package()
        marker = self.root / "outside-marker.md"
        marker.write_text("FOREIGN_MARKER", encoding="utf-8")
        source = fake / "allgemein/regeln/kern.md"
        parked = fake / "allgemein/regeln/kern.parked"
        original_read = builder.read_relative

        def swap_during_read(package_fd, relative, expected):
            if relative != Path("allgemein/regeln/kern.md"):
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
            (fake / "allgemein/regeln/kern.md").write_text("# Changed\n", encoding="utf-8")
            return "ja"

        with patch.object(builder, "PACKAGE", fake), patch("builtins.input", side_effect=change_after_preview):
            result = builder.main(["--destination", str(self.destination), "--apply"])
        self.assertEqual(result, 1)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
