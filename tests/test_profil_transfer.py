import json
import importlib.util
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "profil_transfer.py"
FIELDS = {
    "name_anrede": "Alex",
    "rolle": "Entwickler",
    "sprache": "Deutsch",
    "zeitzone": "Europe/Berlin",
    "arbeitszeiten": "Montag bis Freitag",
    "arbeitsweise": "Kurze Antworten",
    "prioritaeten": "Qualität",
}
LABELS = ["Name und Anrede", "Rolle", "Sprache", "Zeitzone", "Arbeitszeiten und freie Tage", "Arbeitsweise", "Prioritäten"]


def profile_text(values=None):
    values = values or list(FIELDS.values())
    rows = "\n".join(f"| {label} | {value} |" for label, value in zip(LABELS, values))
    return f"# Persönliches Profil\n\n| Feld | Bestätigter Wert |\n| --- | --- |\n{rows}\n\n## Kleine Vorlieben\n\n| Vorliebe | Datum | Grundlage |\n| --- | --- | --- |\n| Kurz | 2026-10-19 | ausdrücklich |\n\n## Bestätigte Änderungen\n\nGeheime Notiz bleibt zurück.\n"


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=SCRIPT.parents[1])
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "profil.md").write_text(profile_text(), encoding="utf-8")
        (self.source / ".env").write_text("SECRET=do-not-read", encoding="utf-8")
        (self.source / "pfade.json").write_text('{"path":"/private/source"}', encoding="utf-8")
        (self.source / "projekte.md").write_text("Private project", encoding="utf-8")
        self.export_file = self.root / "transfer.json"

    def run_cli(self, *args, answer=""):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], input=answer, text=True, capture_output=True)

    def test_preview_read_only_and_cancel(self):
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ausgeschlossen", result.stdout)
        self.assertFalse(self.export_file.exists())
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="nein\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.export_file.exists())

    def test_export_import_main_path_and_file_preservation(self):
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = json.loads(self.export_file.read_text(encoding="utf-8"))
        self.assertEqual(doc["profile"], FIELDS)
        self.assertEqual(len(doc["vorlieben"]), 1)
        self.assertNotIn("SECRET", self.export_file.read_text())
        self.assertNotIn("/private/source", self.export_file.read_text())
        self.assertNotIn("Geheime Notiz", self.export_file.read_text())
        self.assertEqual(stat.S_IMODE(self.export_file.stat().st_mode), 0o600)
        dest = self.root / "dest"
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(dest.exists())
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)
        self.assertIn("Alex", (dest / "profil.md").read_text())
        self.assertFalse((dest / "pfade.json").exists())
        self.assertFalse((dest / "projekte.md").exists())
        self.assertFalse((dest / ".env").exists())

    def test_conflict_backup_and_other_files_preserved(self):
        self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="ja\n")
        dest = self.root / "dest"
        dest.mkdir()
        existing = profile_text(["Alt", *list(FIELDS.values())[1:]])
        (dest / "profil.md").write_text(existing)
        (dest / "pfade.json").write_text("local-only")
        preview = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest)
        self.assertIn("Alt -> Alex", preview.stdout)
        self.assertEqual((dest / "profil.md").read_text(), existing)
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list(dest.glob("profil.md.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), existing)
        self.assertEqual(stat.S_IMODE(backups[0].stat().st_mode), 0o600)
        self.assertEqual((dest / "pfade.json").read_text(), "local-only")

    def test_rejects_malformed_unknown_duplicate_and_symlinks(self):
        dest = self.root / "dest"
        for content in ('{"schema_version":1,"schema_version":1}', '{"schema_version":1,"profile":{},"vorlieben":[],"secret":"x"}', "garbage"):
            self.export_file.write_text(content)
            result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--apply", answer="ja\n")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(dest.exists())
        self.export_file.unlink()
        self.export_file.symlink_to(self.source / "profil.md")
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest)
        self.assertNotEqual(result.returncode, 0)
        self.export_file.unlink()
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        dest.mkdir()
        (dest / "profil.md").symlink_to(self.source / "profil.md")
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--apply", answer="ja\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(list(dest.glob("profil.md.backup-*")))

    def test_secret_files_are_never_opened(self):
        # A broken symlink fails if followed. Only profil.md is an input to export.
        (self.source / ".env").unlink()
        (self.source / ".env").symlink_to(self.root / "missing-secret")
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="ja\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_changed_source_after_preview_is_rejected(self):
        spec = importlib.util.spec_from_file_location("profil_transfer_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def change_and_confirm(_prompt):
            path = self.source / "profil.md"
            path.write_text(profile_text().replace("Qualität", "Tempo"), encoding="utf-8")
            return "ja"

        args = SimpleNamespace(profile_dir=str(self.source), output=str(self.export_file), apply=True)
        with patch("builtins.input", side_effect=change_and_confirm), redirect_stdout(StringIO()):
            with self.assertRaises(module.TransferError):
                module.export(args)
        self.assertFalse(self.export_file.exists())

    def test_existing_pid_temp_file_is_preserved(self):
        self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="ja\n")
        dest = self.root / "dest"
        dest.mkdir()
        (dest / "profil.md").write_text(profile_text(), encoding="utf-8")
        # A fixed PID name can exist before import. It must never be deleted.
        marker = dest / f".profil.md.import-{os.getpid()}"
        marker.write_text("keep me", encoding="utf-8")
        spec = importlib.util.spec_from_file_location("profil_transfer_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = SimpleNamespace(input=str(self.export_file), profile_dir=str(dest), apply=True)
        with patch("builtins.input", return_value="ja"), redirect_stdout(StringIO()):
            module.import_profile(args)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep me")
        self.assertEqual(len(list(dest.glob(".profil.md.import-*"))), 1)

    def test_control_characters_are_rejected_before_preview(self):
        self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="ja\n")
        dest = self.root / "dest"
        for bad in ("\x00", "\x1b[31m", "\x85", "\u202e", "\u2028", "\u2029", "\ud800"):
            doc = json.loads(self.export_file.read_text(encoding="utf-8"))
            doc["profile"]["rolle"] = "unsafe" + bad
            self.export_file.write_text(json.dumps(doc), encoding="utf-8")
            result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertFalse(dest.exists())

    def test_export_size_cannot_exceed_own_import_limit(self):
        spec = importlib.util.spec_from_file_location("profil_transfer_size_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        doc = {"schema_version": 1, "profile": FIELDS,
               "vorlieben": [{"vorliebe": "a" * 1250, "datum": "", "grundlage": ""} for _ in range(100)]}
        markdown = module.render_profile(doc)
        self.assertLess(len(markdown), module.MAX_BYTES)
        self.assertGreater(len(module.render_export(doc)), module.MAX_BYTES)
        (self.source / "profil.md").write_bytes(markdown)
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="ja\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.export_file.exists())
        self.assertEqual(result.stdout, "")

    def test_import_rejects_markdown_that_would_exceed_read_limit(self):
        doc = {"schema_version": 1, "profile": FIELDS,
               "vorlieben": [{"vorliebe": "|" * 900, "datum": "", "grundlage": ""} for _ in range(100)]}
        self.export_file.write_text(json.dumps(doc), encoding="utf-8")
        self.assertLess(self.export_file.stat().st_size, 128 * 1024)
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", self.root / "dest", "--apply", answer="ja\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "dest").exists())


if __name__ == "__main__":
    unittest.main()
