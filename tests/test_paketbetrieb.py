"""Ausschließlich synthetische Paketquellen, Profile und Clientordner."""
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "scripts"))
import installieren
import installationsplan
import paket_bauen
import paketbestand as bestand
import paketbetrieb as betrieb
import einrichtungsstatus


class PackageOperationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=PACKAGE.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.source = self.root / "source"
        (self.source / "scripts").mkdir(parents=True)
        for name in paket_bauen.SCRIPT_NAMES:
            (self.source / "scripts" / name).write_bytes((PACKAGE / "scripts" / name).read_bytes())
        self.put_source("allgemein/regeln/kern.md", b"# Synthetic core\n")
        self.put_source("allgemein/skills/alpha/SKILL.md", b"alpha")
        self.put_source("allgemein/skills/alpha/old.txt", b"old")
        self.profile = self.home / "profile"
        self.profile.mkdir()
        self.config_path = self.profile / "pfade.json"
        self.config = {"schema_version": 1, "confirmed": True, "clients": ["codex", "claude-code"],
                       "paths": {"source": str(self.source), "runtime": "~/runtime", "profile": "~/profile",
                                 "output": "~/output", "coding_roots": [], "customer_roots": []}}
        self.config_path.write_bytes(bestand.encoded(self.config))
        self.markers = {}
        for path in (self.profile / "profil.md", self.profile / ".env", self.profile / "wissen/notiz.md",
                     self.profile / "journal/privat.json", self.home / "output/result.txt"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"SYNTHETIC_PRIVATE_MARKER")
            self.markers[path] = path.read_bytes()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(paket_bauen, "PACKAGE", self.source))
        self.stack.enter_context(patch.object(installationsplan, "SKILLS", self.source / "allgemein/skills"))
        self.stack.enter_context(patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}))
        self.state_dir = self.profile / "zustand"
        self.runtime = self.home / "runtime"

    def put_source(self, relative, value):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)

    def install(self, custom=False):
        args = ["--config", str(self.config_path), "--home", str(self.home), "--apply"]
        if custom:
            args += ["--codex-home", str(self.home / "custom-codex"), "--claude-config-dir", str(self.home / "custom-claude")]
        with patch("builtins.input", return_value="ja"), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
            result = installieren.main(args)
        self.assertEqual(result, 0, errors.getvalue())

    def changed_source(self):
        self.put_source("allgemein/skills/alpha/SKILL.md", b"changed alpha")
        self.put_source("allgemein/regeln/kern.md", b"# Changed synthetic core\n")
        (self.source / "allgemein/skills/alpha/old.txt").unlink()
        self.put_source("allgemein/skills/beta/SKILL.md", b"beta")

    def plan(self, action="update"):
        return betrieb.plan(action, self.config_path, self.home)

    def run_operation(self, action="update"):
        planned = self.plan(action)
        betrieb.execute(planned, self.config_path, self.home)
        return planned

    def assert_private_unchanged(self):
        for path, value in self.markers.items():
            self.assertEqual(path.read_bytes(), value)

    def test_install_update_status_uninstall_with_private_read_guard(self):
        self.install(custom=True)
        self.changed_source()
        foreign = self.runtime / "allgemein/skills/alpha/foreign.txt"
        foreign.write_bytes(b"foreign")
        before_manifest = bestand.read_snapshot(self.state_dir / "bestand.json")[0]
        original_open = os.open
        private_strings = {str(path) for path in self.markers}
        private_inodes = {path.stat().st_ino for path in self.markers}
        original_read = os.read
        def guarded_read(fd, size):
            self.assertNotIn(os.fstat(fd).st_ino, private_inodes, "Privater Inhalt gelesen")
            return original_read(fd, size)
        with patch.object(os, "read", side_effect=guarded_read):
            planned = self.plan()
            self.assertEqual({step["kind"] for step in planned["steps"]}, {"add", "replace", "remove", "keep"})
            self.assertEqual(bestand.read_snapshot(self.state_dir / "bestand.json")[0], before_manifest)
            betrieb.execute(planned, self.config_path, self.home)
            self.assertEqual(einrichtungsstatus.inspect(self.config_path, self.home)["status"], "vorhanden")
            self.assertTrue((self.home / "custom-codex/AGENTS.md").is_file())
            self.assertTrue((self.home / ".agents/skills/beta").is_symlink())
            self.assertEqual(len(list((self.state_dir / "sicherungen").glob("*/*.md"))), 2)
            self.run_operation("uninstall")
            self.assertEqual(einrichtungsstatus.inspect(self.config_path, self.home)["status"], "deinstalliert")
        self.assertEqual(foreign.read_bytes(), b"foreign")
        self.assertTrue(self.runtime.is_dir())
        self.assertTrue(self.profile.is_dir())
        self.assertTrue((self.home / "output").is_dir())
        self.assert_private_unchanged()
        with self.assertRaises(bestand.BestandError):
            self.plan("uninstall")

    def test_bundled_v2_status_from_other_directory(self):
        self.install()
        result = subprocess.run([sys.executable, str(self.runtime / "scripts/einrichtungsstatus.py"),
                                 "--config", str(self.config_path), "--home", str(self.home), "--json"],
                                cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "vorhanden")

    def test_all_own_roles_modified_or_missing_block_before_mutation(self):
        self.install()
        for target in (self.runtime / "allgemein/regeln/kern.md", self.home / ".codex/AGENTS.md"):
            original = target.read_bytes()
            target.write_bytes(b"local edit")
            with self.assertRaises(bestand.BestandError):
                self.plan("uninstall")
            target.unlink()
            with self.assertRaises(FileNotFoundError):
                self.plan()
            target.write_bytes(original)
        link = self.home / ".agents/skills/alpha"
        link.unlink()
        link.symlink_to(self.home / "output")
        with self.assertRaises(bestand.BestandError):
            self.plan("uninstall")
        self.assertFalse((self.state_dir / "operation.json").exists())
        self.assert_private_unchanged()

    def test_unknown_new_target_blocks(self):
        self.install()
        self.changed_source()
        target = self.runtime / "allgemein/skills/beta/SKILL.md"
        target.parent.mkdir()
        target.write_bytes(b"foreign")
        with self.assertRaises(bestand.BestandError):
            self.plan()
        self.assertEqual(target.read_bytes(), b"foreign")

    def test_preview_and_cancel_have_no_mutation(self):
        self.install()
        self.changed_source()
        before = (self.state_dir / "bestand.json").read_bytes()
        args = ["--config", str(self.config_path), "--home", str(self.home)]
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(betrieb.main("update", args), 0)
        self.assertIn("Manifest SHA256", output.getvalue())
        self.assertIn(str(self.runtime / "allgemein/skills/beta/SKILL.md"), output.getvalue())
        with patch("builtins.input", return_value="nein"), redirect_stdout(io.StringIO()):
            self.assertEqual(betrieb.main("update", args + ["--apply"]), 0)
        self.assertEqual((self.state_dir / "bestand.json").read_bytes(), before)
        self.assertFalse((self.state_dir / "operation.json").exists())

    def test_raced_target_after_preview_preserved(self):
        self.install()
        self.changed_source()
        planned = self.plan()
        target = self.runtime / "allgemein/skills/alpha/SKILL.md"
        target.write_bytes(b"foreign replacement")
        with self.assertRaises(bestand.BestandError):
            betrieb.execute(planned, self.config_path, self.home)
        self.assertEqual(target.read_bytes(), b"foreign replacement")
        self.assertFalse((self.state_dir / "operation.json").exists())

    def test_mid_operation_failure_preserves_old_bestand_and_blocks_repeat(self):
        self.install()
        self.changed_source()
        before = (self.state_dir / "bestand.json").read_bytes()
        original = betrieb.mutate
        count = 0
        def failing(step, data=None, **kwargs):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError("synthetic interruption")
            return original(step, data, **kwargs)
        with patch.object(betrieb, "mutate", side_effect=failing):
            with self.assertRaises(OSError):
                self.run_operation()
        self.assertEqual((self.state_dir / "bestand.json").read_bytes(), before)
        operation = json.loads((self.state_dir / "operation.json").read_bytes())
        self.assertEqual(operation["status"], "interrupted")
        self.assertIn("done", {step["status"] for step in operation["steps"]})
        self.assertEqual(einrichtungsstatus.inspect(self.config_path, self.home)["status"], "eingeschränkt")
        with self.assertRaises(bestand.BestandError):
            self.plan()
        self.assert_private_unchanged()

    def test_commit_failure_preserves_old_bestand_and_blocks_repeat(self):
        self.install()
        self.changed_source()
        before = (self.state_dir / "bestand.json").read_bytes()
        original = bestand.publish
        def failing(path, value, previous=None):
            if Path(path).name == "bestand.json":
                raise OSError("synthetic state commit failure")
            return original(path, value, previous)
        with patch.object(bestand, "publish", side_effect=failing):
            with self.assertRaises(OSError):
                self.run_operation()
        self.assertEqual((self.state_dir / "bestand.json").read_bytes(), before)
        self.assertEqual(einrichtungsstatus.inspect(self.config_path, self.home)["status"], "eingeschränkt")
        with self.assertRaises(bestand.BestandError):
            self.plan()

    def test_custom_binding_conflict_and_wrong_home_stop(self):
        self.install(custom=True)
        self.assertEqual(einrichtungsstatus.inspect(self.config_path, self.home)["status"], "vorhanden")
        with self.assertRaises(bestand.BestandError):
            betrieb.plan("uninstall", self.config_path, self.home, str(self.home / ".codex"))
        wrong_home = self.root / "wrong-home"
        wrong_home.mkdir()
        with self.assertRaises((bestand.BestandError, FileNotFoundError)):
            betrieb.plan("uninstall", self.config_path, wrong_home)

    def test_legacy_state_is_readonly_and_not_migrated(self):
        self.install()
        (self.state_dir / "bestand.json").unlink()
        self.assertEqual(einrichtungsstatus.inspect(self.config_path, self.home)["status"], "vorhanden")
        with self.assertRaises(FileNotFoundError):
            self.plan("uninstall")
        self.assertFalse((self.state_dir / "bestand.json").exists())

    def test_second_apply_no_changes_is_verified_and_no_blind_replay(self):
        self.install()
        self.changed_source()
        self.run_operation()
        planned = self.plan()
        self.assertEqual({step["kind"] for step in planned["steps"]}, {"keep"})
        before = {path: bestand.check_target(path, item) for path, item in planned["old"]["owned"].items()}
        betrieb.execute(planned, self.config_path, self.home)
        self.assertEqual(before, {path: bestand.check_target(path, item) for path, item in planned["old"]["owned"].items()})

    def test_source_change_after_confirmation_stops(self):
        self.install()
        planned = self.plan()
        self.changed_source()
        with self.assertRaises(bestand.BestandError):
            betrieb.execute(planned, self.config_path, self.home)
        self.assertFalse((self.state_dir / "operation.json").exists())


if __name__ == "__main__":
    unittest.main()
