"""Update of a real 0.1.7-dev installation (German layout, old script names) to the current package.

The old package comes from git commit e9c9133, the last commit with the old layout. The test installs it
with its own installer into a synthetic home, then replaces the source checkout with the current tree, as a
`git pull` would, and runs the current update. Only temporary synthetic folders are used.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
OLD_COMMIT = "e9c9133"
OLD_SCRIPTS = {"einrichten.py", "profil_transfer.py", "pruefe_konfiguration.py", "pruefe_register.py",
               "einrichtungsstatus.py", "sichere_dateien.py", "paketregeln.py", "paketbestand.py"}


def git(*args, **kwargs):
    return subprocess.run(["git", "-C", str(PACKAGE), *args], capture_output=True, timeout=60, **kwargs)


class UpdateFrom017Tests(unittest.TestCase):
    def setUp(self):
        if shutil.which("git") is None or git("cat-file", "-e", OLD_COMMIT + "^{commit}").returncode != 0:
            reason = (f"IMPORTANT: the 0.1.7-dev to current update compatibility test DID NOT RUN. "
                      f"git or commit {OLD_COMMIT} is not available (shallow clone?). "
                      f"Fetch the full history and run the suite again before relying on update compatibility.")
            sys.stderr.write("\n" + reason + "\n")
            self.skipTest(reason)
        temporary = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=PACKAGE.parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.source = self.root / "source"
        self.source.mkdir()
        archive = git("archive", "--format=tar", OLD_COMMIT, "scripts", "allgemein")
        self.assertEqual(archive.returncode, 0, archive.stderr)
        extracted = subprocess.run(["tar", "-x", "-C", str(self.source)], input=archive.stdout,
                                   capture_output=True, timeout=60)
        self.assertEqual(extracted.returncode, 0, extracted.stderr)
        self.profile = self.home / "aios-profile"
        self.profile.mkdir()
        self.config_path = self.profile / "pfade.json"
        # Written like a 0.1.7-dev setup: no language field.
        self.config_path.write_text(json.dumps({
            "schema_version": 1, "confirmed": True, "clients": ["claude-code", "codex"],
            "paths": {"source": str(self.source), "runtime": "~/aios-runtime", "profile": "~/aios-profile",
                      "output": "~/aios-output", "coding_roots": [], "customer_roots": []}}), encoding="utf-8")
        (self.profile / "profil.md").write_bytes(b"SYNTHETIC_PRIVATE_MARKER")
        self.env = {key: value for key, value in os.environ.items() if key not in ("CODEX_HOME", "CLAUDE_CONFIG_DIR")}
        self.runtime = self.home / "aios-runtime"
        self.args = ["--config", str(self.config_path), "--home", str(self.home)]

    def run_script(self, name, *extra, answer=""):
        return subprocess.run([sys.executable, "-B", str(self.source / "scripts" / name), *self.args, *extra],
                              input=answer, capture_output=True, text=True, env=self.env, timeout=120)

    def pull_current_tree(self):
        shutil.rmtree(self.source / "scripts")
        shutil.rmtree(self.source / "allgemein")
        (self.source / "scripts").mkdir()
        for script in (PACKAGE / "scripts").glob("*.py"):
            shutil.copy2(script, self.source / "scripts" / script.name)
        shutil.copytree(PACKAGE / "de", self.source / "de", ignore=shutil.ignore_patterns("__pycache__"))

    def install_old(self):
        installed = self.run_script("installieren.py", "--apply", answer="ja\n")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        old_manifest = json.loads((self.runtime / "paket.json").read_text(encoding="utf-8"))
        self.assertEqual(old_manifest["version"], "0.1.7-dev")
        self.assertNotIn("language", old_manifest)
        self.assertEqual({path.name for path in (self.runtime / "scripts").iterdir()}, OLD_SCRIPTS)
        return (self.home / ".claude/CLAUDE.md").read_bytes()

    def update_with_old_code(self):
        """A real-world 0.1.7 state: already updated once by the old code, with backups and journal."""
        core = self.source / "allgemein/regeln/kern.md"
        core.write_bytes(core.read_bytes() + b"\nSynthetische Zwischenfassung.\n")
        updated = self.run_script("aktualisieren.py", "--apply", answer="ja\n")
        self.assertEqual(updated.returncode, 0, updated.stderr)
        operation = json.loads((self.profile / "zustand/operation.json").read_text(encoding="utf-8"))
        self.assertEqual(operation["status"], "completed")
        self.assertEqual(len(list((self.profile / "zustand/sicherungen").glob("*/*.md"))), 2)
        self.assertIn("Synthetische Zwischenfassung.", (self.home / ".codex/AGENTS.md").read_text(encoding="utf-8"))
        return operation["id"]

    def update_and_check(self, old_rule, previous_operation=None):
        self.pull_current_tree()
        preview = self.run_script("update.py")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        for name in OLD_SCRIPTS:
            self.assertIn(f"remove: {self.runtime / 'scripts' / name}", preview.stdout)
        self.assertIn(f"add: {self.runtime / 'scripts/setup_status.py'}", preview.stdout)
        self.assertIn(f"add: {self.runtime / 'scripts/languages.py'}", preview.stdout)
        self.assertIn("old: 0.1.7-dev (de)", preview.stdout)

        updated = self.run_script("update.py", "--apply", answer="yes\n")
        self.assertEqual(updated.returncode, 0, updated.stderr)
        new_manifest = json.loads((self.runtime / "paket.json").read_text(encoding="utf-8"))
        self.assertEqual(new_manifest["language"], "de")
        self.assertNotEqual(new_manifest["version"], "0.1.7-dev")
        scripts = {path.name for path in (self.runtime / "scripts").iterdir()}
        self.assertFalse(scripts & OLD_SCRIPTS)
        self.assertIn("setup_status.py", scripts)
        self.assertIn("languages.py", scripts)
        self.assertTrue((self.runtime / "allgemein/regeln/kern.md").is_file())
        state = json.loads((self.profile / "zustand/bestand.json").read_text(encoding="utf-8"))
        self.assertEqual(state["manifest"]["language"], "de")
        operation = json.loads((self.profile / "zustand/operation.json").read_text(encoding="utf-8"))
        self.assertEqual(operation["status"], "completed")
        self.assertEqual(operation["action"], "update")
        self.assertNotEqual(operation["id"], previous_operation)
        unchanged_core = (PACKAGE / "de/regeln/kern.md").read_bytes() == git(
            "show", f"{OLD_COMMIT}:allgemein/regeln/kern.md").stdout
        for client_rule in (self.home / ".claude/CLAUDE.md", self.home / ".codex/AGENTS.md"):
            rule = client_rule.read_text(encoding="utf-8")
            self.assertTrue(rule.startswith("<!-- Generiert aus allgemein/regeln/kern.md. SHA256: "))
            self.assertIn("Lokale Konfiguration: [pfade.json](<", rule)
            self.assertIn("Profil: [profil.md](<", rule)
            self.assertNotIn("Synthetische Zwischenfassung.", rule)
            if unchanged_core:
                self.assertEqual(rule.encode("utf-8"), old_rule)
        skill_names = sorted(path.parent.name for path in (self.runtime / "allgemein/skills").glob("*/SKILL.md"))
        self.assertEqual(len(skill_names), 21)
        for name in skill_names:
            for link in (self.home / ".claude/skills" / name, self.home / ".agents/skills" / name):
                self.assertEqual(os.readlink(link), str(self.runtime / "allgemein/skills" / name))

        status = subprocess.run([sys.executable, "-B", str(self.runtime / "scripts/setup_status.py"),
                                 *self.args, "--json"], capture_output=True, text=True, env=self.env, timeout=30)
        self.assertEqual(status.returncode, 0, status.stderr)
        value = json.loads(status.stdout)
        self.assertEqual(value["status"], "present")
        self.assertTrue(all(item["skills"] == 21 for item in value["clients"]))
        self.assertEqual((self.profile / "profil.md").read_bytes(), b"SYNTHETIC_PRIVATE_MARKER")

    def test_update_replaces_old_runtime_scripts_and_keeps_german_layout(self):
        old_rule = self.install_old()
        self.update_and_check(old_rule)
        uninstall = self.run_script("uninstall.py", "--apply", answer="yes\n")
        self.assertEqual(uninstall.returncode, 0, uninstall.stderr)
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())
        self.assertFalse(any((self.runtime / "scripts").glob("*.py")) if (self.runtime / "scripts").exists() else False)

    def test_update_after_previous_update_by_old_code(self):
        old_rule = self.install_old()
        previous = self.update_with_old_code()
        self.update_and_check(old_rule, previous)
        backups = list((self.profile / "zustand/sicherungen").glob("*/*.md"))
        self.assertEqual(len(backups), 4)
        self.assertTrue(any("Synthetische Zwischenfassung." in path.read_text(encoding="utf-8") for path in backups))


if __name__ == "__main__":
    unittest.main()
