import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import einrichten


class EinrichtungTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "home"
        self.home.mkdir()
        self.source = Path(self.temporary.name) / "source"
        self.source.mkdir()
        self.target = self.home / "aios-profile"

    def run_cli(self, confirm="ja", key_choice="nein", key=""):
        answers = iter([
            "beide", str(self.source), "", "", "", "", "",
            "Alex", "Beratung", "Deutsch", "Europe/Berlin", "", "", "",
            confirm, key_choice,
        ])
        out, err = io.StringIO(), io.StringIO()
        with patch("builtins.input", side_effect=lambda prompt="": next(answers)), \
             patch.object(einrichten.getpass, "getpass", return_value=key), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = einrichten.main(["--home", str(self.home)])
        return status, out.getvalue(), err.getvalue()

    def test_preview_cancellation_writes_nothing(self):
        status, output, error = self.run_cli(confirm="nein")
        self.assertEqual(status, 0, error)
        self.assertIn("Vorschau", output)
        self.assertIn('"confirmed": false', output)
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_main_path_creates_only_private_profile(self):
        status, output, error = self.run_cli()
        self.assertEqual(status, 0, error)
        self.assertTrue(self.target.is_dir())
        config = json.loads((self.target / "pfade.json").read_text())
        self.assertTrue(config["confirmed"])
        self.assertEqual(config["clients"], ["claude-code", "codex"])
        self.assertIn("| Name und Anrede | Alex |", (self.target / "profil.md").read_text())
        self.assertIn("BLOCKBRAIN_API_KEY=\n", (self.target / ".env").read_text())
        self.assertTrue((self.target / "projekte.md").is_file())
        self.assertTrue((self.target / "wissen/INDEX.md").is_file())
        self.assertFalse((self.home / "aios-runtime").exists())
        self.assertFalse((self.home / "aios-output").exists())
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o700)
        for file in self.target.rglob("*"):
            self.assertEqual(file.stat().st_mode & 0o777, 0o700 if file.is_dir() else 0o600)

    def test_existing_env_is_preserved(self):
        self.target.mkdir()
        env = self.target / ".env"
        env.write_text("KEEP=secret\n")
        status, output, error = self.run_cli()
        self.assertEqual(status, 1)
        self.assertEqual(env.read_text(), "KEEP=secret\n")
        self.assertEqual(list(self.target.iterdir()), [env])

    def test_key_not_printed(self):
        secret = "synthetic-private-token"
        status, output, error = self.run_cli(key_choice="ja", key=secret)
        self.assertEqual(status, 0, error)
        self.assertNotIn(secret, output + error)
        self.assertIn(secret, (self.target / ".env").read_text())

    def test_profile_values_roundtrip_through_export_and_import(self):
        values = {label: r"Ordner C:\work | Format **kurz**" for label, _ in einrichten.FIELDS}
        doc = einrichten.profil.parse_profile(einrichten.profile_text(values).encode("utf-8"))
        self.assertEqual(list(doc["profile"].values()), list(values.values()))
        self.assertEqual(einrichten.profil.parse_profile(einrichten.profil.render_profile(doc)), doc)

    def test_invalid_profile_values_rejected_before_writing(self):
        for value in ["x" * 4097, "mehr\nzeilig", "test\x00", "test\x1b[2J"]:
            with self.subTest(value=repr(value[:20])), self.assertRaises(einrichten.profil.TransferError):
                einrichten.profile_text({"Name und Anrede": value})
        self.assertFalse(self.target.exists())

    def test_symlink_target_rejected(self):
        elsewhere = Path(self.temporary.name) / "elsewhere"
        elsewhere.mkdir()
        self.target.symlink_to(elsewhere, target_is_directory=True)
        status, output, error = self.run_cli()
        self.assertEqual(status, 1)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_help_has_no_effect(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as exit_info:
            einrichten.main(["--help"])
        self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
