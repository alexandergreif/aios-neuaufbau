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


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "profile_transfer.py"
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


EN_LABELS = ["Name and form of address", "Role", "Language", "Time zone", "Working hours and days off",
             "Working style", "Priorities"]


def load_module(name):
    with patch.object(sys, "path", [str(SCRIPT.parent), *sys.path]):
        spec = importlib.util.spec_from_file_location(name, SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


def english_profile_text(values=None):
    values = values or list(FIELDS.values())
    rows = "\n".join(f"| {label} | {value} |" for label, value in zip(EN_LABELS, values))
    return f"# Personal profile\n\n| Field | Confirmed value |\n| --- | --- |\n{rows}\n\n## Small preferences\n\n| Preference | Date | Basis |\n| --- | --- | --- |\n| Short | 2026-10-19 | explicit |\n\n## Confirmed changes\n\nSecret note stays behind.\n"


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=SCRIPT.parents[1])
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
        self.assertIn("Excluded", result.stdout)
        self.assertFalse(self.export_file.exists())
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="no\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.export_file.exists())

    def test_export_import_main_path_and_file_preservation(self):
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = json.loads(self.export_file.read_text(encoding="utf-8"))
        self.assertEqual(doc["profile"], FIELDS)
        self.assertEqual(len(doc["vorlieben"]), 1)
        self.assertNotIn("SECRET", self.export_file.read_text())
        self.assertNotIn("/private/source", self.export_file.read_text())
        self.assertNotIn("Geheime Notiz", self.export_file.read_text())
        self.assertEqual(stat.S_IMODE(self.export_file.stat().st_mode), 0o600)
        dest = self.root / "dest"
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--language", "de")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(dest.exists())
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--language", "de",
                              "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)
        self.assertIn("Alex", (dest / "profil.md").read_text())
        self.assertFalse((dest / "pfade.json").exists())
        self.assertFalse((dest / "projekte.md").exists())
        self.assertFalse((dest / ".env").exists())

    def test_conflict_backup_and_other_files_preserved(self):
        self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
        dest = self.root / "dest"
        dest.mkdir()
        existing = profile_text(["Alt", *list(FIELDS.values())[1:]])
        (dest / "profil.md").write_text(existing)
        (dest / "pfade.json").write_text("local-only")
        preview = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest)
        self.assertIn("Alt -> Alex", preview.stdout)
        self.assertEqual((dest / "profil.md").read_text(), existing)
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--apply", answer="yes\n")
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
            result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--apply", answer="yes\n")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(dest.exists())
        self.export_file.unlink()
        self.export_file.symlink_to(self.source / "profil.md")
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest)
        self.assertNotEqual(result.returncode, 0)
        self.export_file.unlink()
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        dest.mkdir()
        (dest / "profil.md").symlink_to(self.source / "profil.md")
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest, "--apply", answer="yes\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(list(dest.glob("profil.md.backup-*")))

    def test_secret_files_are_never_opened(self):
        # A broken symlink fails if followed. Only profil.md is an input to export.
        (self.source / ".env").unlink()
        (self.source / ".env").symlink_to(self.root / "missing-secret")
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_changed_source_after_preview_is_rejected(self):
        module = load_module("profile_transfer_test")

        def change_and_confirm(_prompt):
            path = self.source / "profil.md"
            path.write_text(profile_text().replace("Qualität", "Tempo"), encoding="utf-8")
            return "yes"

        args = SimpleNamespace(profile_dir=str(self.source), output=str(self.export_file), apply=True)
        with patch("builtins.input", side_effect=change_and_confirm), redirect_stdout(StringIO()):
            with self.assertRaises(module.TransferError):
                module.export(args)
        self.assertFalse(self.export_file.exists())

    def test_existing_pid_temp_file_is_preserved(self):
        self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
        dest = self.root / "dest"
        dest.mkdir()
        (dest / "profil.md").write_text(profile_text(), encoding="utf-8")
        # A fixed PID name can exist before import. It must never be deleted.
        marker = dest / f".profil.md.import-{os.getpid()}"
        marker.write_text("keep me", encoding="utf-8")
        module = load_module("profile_transfer_test")
        args = SimpleNamespace(input=str(self.export_file), profile_dir=str(dest), apply=True)
        with patch("builtins.input", return_value="yes"), redirect_stdout(StringIO()):
            module.import_profile(args)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep me")
        self.assertEqual(len(list(dest.glob(".profil.md.import-*"))), 1)

    def test_control_characters_are_rejected_before_preview(self):
        self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
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
        module = load_module("profile_transfer_size_test")
        doc = {"schema_version": 1, "profile": FIELDS,
               "vorlieben": [{"vorliebe": "a" * 1250, "datum": "", "grundlage": ""} for _ in range(100)]}
        markdown = module.render_profile(doc)
        self.assertLess(len(markdown), module.MAX_BYTES)
        self.assertGreater(len(module.render_export(doc)), module.MAX_BYTES)
        (self.source / "profil.md").write_bytes(markdown)
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.export_file.exists())
        self.assertEqual(result.stdout, "")

    def test_import_rejects_markdown_that_would_exceed_read_limit(self):
        doc = {"schema_version": 1, "profile": FIELDS,
               "vorlieben": [{"vorliebe": "|" * 900, "datum": "", "grundlage": ""} for _ in range(100)]}
        self.export_file.write_text(json.dumps(doc), encoding="utf-8")
        self.assertLess(self.export_file.stat().st_size, 128 * 1024)
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", self.root / "dest", "--apply", answer="yes\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "dest").exists())

    def test_english_profile_export_and_cross_language_import(self):
        source = self.root / "en-source"
        source.mkdir()
        (source / "profile.md").write_text(english_profile_text(), encoding="utf-8")
        (source / "paths.json").write_text('{"path":"/private/source"}', encoding="utf-8")
        result = self.run_cli("export", "--profile-dir", source, "--output", self.export_file, "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("paths.json, projects.md", result.stdout)
        doc = json.loads(self.export_file.read_text(encoding="utf-8"))
        self.assertEqual(doc["profile"], FIELDS)
        self.assertEqual(doc["vorlieben"], [{"vorliebe": "Short", "datum": "2026-10-19", "grundlage": "explicit"}])
        self.assertNotIn("Secret note", self.export_file.read_text())
        german = self.root / "de-dest"
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", german, "--language", "de",
                              "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("| Name und Anrede | Alex |", (german / "profil.md").read_text())
        english = self.root / "en-dest"
        english.mkdir()
        (english / "paths.json").write_text("local-only", encoding="utf-8")
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", english, "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (english / "profile.md").read_text()
        self.assertIn("# Personal profile", text)
        self.assertIn("| Name and form of address | Alex |", text)
        self.assertIn("## Small preferences", text)
        self.assertEqual((english / "paths.json").read_text(), "local-only")
        self.assertFalse((english / "profil.md").exists())
        explicit = self.root / "explicit"
        result = self.run_cli("import", "--input", self.export_file, "--profile-dir", explicit, "--language", "en",
                              "--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((explicit / "profile.md").is_file())

    def test_mixed_language_profile_folder_needs_explicit_language(self):
        (self.source / "profile.md").write_text(english_profile_text(), encoding="utf-8")
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--language", result.stderr)
        result = self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--language", "en")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_new_or_empty_profile_folder_requires_language(self):
        self.run_cli("export", "--profile-dir", self.source, "--output", self.export_file, "--apply", answer="yes\n")
        for dest, create in ((self.root / "new-dest", False), (self.root / "empty-dest", True)):
            with self.subTest(dest=dest.name):
                if create:
                    dest.mkdir()
                result = self.run_cli("import", "--input", self.export_file, "--profile-dir", dest,
                                      "--apply", answer="yes\n")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--language de or --language en", result.stderr)
                self.assertEqual(dest.exists(), create)
                if create:
                    self.assertEqual(list(dest.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
