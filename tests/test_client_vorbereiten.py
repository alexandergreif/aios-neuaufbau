import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / "scripts/client_vorbereiten.py"
CORE = PACKAGE / "allgemein/regeln/kern.md"


class ClientPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=PACKAGE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.destination = self.root / "isolated"

    def run_cli(self, *args, answer=""):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            input=answer,
            capture_output=True,
            text=True,
        )

    def test_preview_and_cancel_do_not_write(self):
        preview = self.run_cli("--destination", self.destination)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn("Keine Dateien angelegt", preview.stdout)
        self.assertFalse(self.destination.exists())
        cancel = self.run_cli("--destination", self.destination, "--apply", answer="nein\n")
        self.assertEqual(cancel.returncode, 0, cancel.stderr)
        self.assertFalse(self.destination.exists())

    def test_generated_core_and_references(self):
        result = self.run_cli("--destination", self.destination, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = {
            "AGENTS.md",
            "CLAUDE.md",
            "allgemein/regeln/kern.md",
            "allgemein/referenzen/externes-schreiben.md",
            "allgemein/referenzen/profil-und-wissen.md",
        }
        actual = {str(p.relative_to(self.destination)) for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(actual, expected)
        source = CORE.read_bytes()
        self.assertEqual((self.destination / "allgemein/regeln/kern.md").read_bytes(), source)
        generated = (self.destination / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(generated, (self.destination / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn(hashlib.sha256(source).hexdigest(), generated)
        self.assertEqual(generated.split("\n\n", 1)[1], source.decode().replace("../referenzen/", "allgemein/referenzen/"))
        self.assertIn("(allgemein/referenzen/externes-schreiben.md)", generated)
        self.assertIn("(allgemein/referenzen/profil-und-wissen.md)", generated)
        self.assertNotIn(str(PACKAGE), generated)

    def test_existing_destination_is_preserved(self):
        self.destination.mkdir()
        marker = self.destination / "keep.txt"
        marker.write_text("unchanged", encoding="utf-8")
        result = self.run_cli("--destination", self.destination, "--apply", answer="ja\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")
        self.assertEqual(list(self.destination.iterdir()), [marker])

    def test_symlink_destination_and_parent_are_rejected(self):
        target = self.root / "real"
        target.mkdir()
        self.destination.symlink_to(target, target_is_directory=True)
        result = self.run_cli("--destination", self.destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.destination.unlink()
        link_parent = self.root / "linked"
        link_parent.symlink_to(target, target_is_directory=True)
        result = self.run_cli("--destination", link_parent / "new")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse((target / "new").exists())

    def test_symlink_inside_package_is_rejected_before_read(self):
        scripts = str(PACKAGE / "scripts")
        with patch.object(sys, "path", [scripts, *sys.path]):
            spec = importlib.util.spec_from_file_location("client_vorbereiten_test", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        fake_package = self.root / "fake-package"
        fake_package.mkdir()
        external = self.root / "external-marker"
        (external / "regeln").mkdir(parents=True)
        (external / "regeln/kern.md").write_text("marker", encoding="utf-8")
        (fake_package / "allgemein").symlink_to(external, target_is_directory=True)
        with patch.object(module, "PACKAGE", fake_package), patch.object(Path, "read_bytes", side_effect=AssertionError("must not read")):
            with self.assertRaises(module.ConfigurationError):
                module.source_contents()


if __name__ == "__main__":
    unittest.main()
