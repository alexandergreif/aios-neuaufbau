import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stderr, redirect_stdout
from urllib.parse import quote


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / "scripts/install.py"


class FirstInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=PACKAGE.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.profile = self.home / "profile"
        self.profile.mkdir()
        self.config_path = self.profile / "pfade.json"
        self.config = {
            "schema_version": 1, "confirmed": True, "clients": ["claude-code", "codex"],
            "paths": {"source": str(PACKAGE), "runtime": "~/runtime", "profile": "~/profile",
                      "output": "~/output", "coding_roots": [], "customer_roots": []},
        }
        self.write_config()
        (self.profile / "profil.md").write_bytes(b"private profile")
        (self.profile / ".env").write_bytes(b"SECRET=synthetic")

    def write_config(self):
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")

    def run_cli(self, *extra, answer=""):
        env = os.environ.copy()
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        return subprocess.run([sys.executable, str(SCRIPT), "--config", str(self.config_path),
                               "--home", str(self.home), *map(str, extra)], input=answer,
                              capture_output=True, text=True, env=env)

    def load_installer(self):
        with patch.object(sys, "path", [str(PACKAGE / "scripts"), *sys.path]):
            spec = importlib.util.spec_from_file_location("install_test", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    def test_preview_and_cancel_write_nothing(self):
        before = sorted(str(path.relative_to(self.home)) for path in self.home.rglob("*"))
        preview = self.run_cli()
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn("Preview", preview.stdout)
        cancel = self.run_cli("--apply", answer="no\n")
        self.assertEqual(cancel.returncode, 0, cancel.stderr)
        self.assertEqual(before, sorted(str(path.relative_to(self.home)) for path in self.home.rglob("*")))
        self.assertFalse((self.profile / "zustand").exists())

    def test_both_clients_install_and_preserve_private_data(self):
        output = self.home / "output"
        output.mkdir()
        marker = output / "marker.txt"
        marker.write_bytes(b"existing output")
        original = {name: (self.profile / name).read_bytes() for name in ("profil.md", ".env", "pfade.json")}
        result = self.run_cli("--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Client and service function unchecked", result.stdout)
        self.assertEqual(marker.read_bytes(), b"existing output")
        for name, value in original.items():
            self.assertEqual((self.profile / name).read_bytes(), value)
        runtime = self.home / "runtime"
        manifest = json.loads((runtime / "paket.json").read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            self.assertEqual(entry["sha256"], hashlib.sha256((runtime / entry["path"]).read_bytes()).hexdigest())
        expected_ref = quote(str(runtime / "allgemein/referenzen/externes-schreiben.md"), safe="/")
        expected_config = quote(str(self.config_path), safe="/")
        expected_profile = quote(str(self.profile / "profil.md"), safe="/")
        for rule in (self.home / ".claude/CLAUDE.md", self.home / ".codex/AGENTS.md"):
            text = rule.read_text(encoding="utf-8")
            self.assertIn(expected_ref, text)
            self.assertIn(expected_config, text)
            self.assertIn(f"Profil: [profil.md](<{expected_profile}>)", text)
            self.assertTrue(text.startswith("<!-- Generiert aus allgemein/regeln/kern.md. SHA256: "))
            self.assertIn(f"Lokale Konfiguration: [pfade.json](<{expected_config}>)", text)
            self.assertNotIn("(../referenzen/", text)
        skill_names = {p.name for p in (runtime / "allgemein/skills").iterdir() if (p / "SKILL.md").is_file()}
        for name in skill_names:
            for link in (self.home / ".claude/skills" / name, self.home / ".agents/skills" / name):
                self.assertTrue(link.is_symlink())
                self.assertEqual(os.readlink(link), str(runtime / "allgemein/skills" / name))
        state = json.loads((self.profile / "zustand/installation.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "installed")
        self.assertEqual(state["clients"], ["claude-code", "codex"])
        self.assertTrue(any(item["type"] == "link" for item in state["created"]))

    def test_foreign_rule_and_runtime_block_before_writes(self):
        (self.home / ".claude").mkdir()
        foreign = self.home / ".claude/CLAUDE.md"
        foreign.write_bytes(b"foreign")
        result = self.run_cli("--apply", answer="yes\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(foreign.read_bytes(), b"foreign")
        self.assertFalse((self.home / "runtime").exists())
        self.assertFalse((self.profile / "zustand").exists())
        foreign.unlink()
        (self.home / "runtime").mkdir()
        marker = self.home / "runtime/keep.txt"
        marker.write_bytes(b"runtime foreign")
        result = self.run_cli("--apply", answer="yes\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(marker.read_bytes(), b"runtime foreign")
        self.assertFalse((self.profile / "zustand").exists())

    def check_hard_stop_at_confirmed_publish(self, after_publish):
        class HardStop(BaseException):
            pass

        installer = self.load_installer()
        original_publish = installer.bestand.publish
        def stop_publish(path, value, *args, **kwargs):
            if Path(path).name == "bestand.json":
                if after_publish:
                    original_publish(path, value, *args, **kwargs)
                raise HardStop()
            return original_publish(path, value, *args, **kwargs)

        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer.bestand, "publish", side_effect=stop_publish), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(HardStop):
                installer.main(["--config", str(self.config_path), "--home", str(self.home), "--apply"])
        state_dir = self.profile / "zustand"
        self.assertEqual(json.loads((state_dir / "installation.json").read_text())["status"], "installing")
        self.assertEqual((state_dir / "bestand.json").exists(), after_publish)
        env = os.environ.copy()
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        status = subprocess.run([sys.executable, str(PACKAGE / "scripts/setup_status.py"),
                                 "--config", str(self.config_path), "--home", str(self.home), "--json"],
                                capture_output=True, text=True, env=env)
        self.assertEqual(status.returncode, 0 if after_publish else 1, status.stderr)
        self.assertEqual(json.loads(status.stdout)["status"], "present" if after_publish else "limited")

    def test_hard_stop_before_confirmed_publish_is_incomplete(self):
        self.check_hard_stop_at_confirmed_publish(False)

    def test_hard_stop_after_confirmed_publish_has_valid_v2_state(self):
        self.check_hard_stop_at_confirmed_publish(True)

    def test_changed_config_or_package_after_preview_stops(self):
        installer = self.load_installer()
        args = ["--config", str(self.config_path), "--home", str(self.home), "--apply"]
        def change_config(_prompt):
            self.config_path.write_text(json.dumps(self.config, indent=2), encoding="utf-8")
            return "yes"
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", side_effect=change_config):
            self.assertEqual(installer.main(args), 1)
        self.assertFalse((self.home / "runtime").exists())
        self.assertFalse((self.profile / "zustand").exists())
        original = installer.paket_bauen.source_snapshot()
        changed = dict(original)
        changed[Path("allgemein/regeln/kern.md")] = (b"changed", (0, 0, 0, 0))
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer.paket_bauen, "source_snapshot", side_effect=[original, changed]):
            self.assertEqual(installer.main(args), 1)
        self.assertFalse((self.home / "runtime").exists())

    def test_failure_after_runtime_records_failed_status(self):
        installer = self.load_installer()
        real_write = installer.write_exclusive
        def fail_rule(path, data, created=None):
            if Path(path).name == "CLAUDE.md":
                raise OSError("synthetic rule failure")
            return real_write(path, data, created=created)
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer, "write_exclusive", side_effect=fail_rule):
            self.assertEqual(installer.main(["--config", str(self.config_path), "--home", str(self.home), "--apply"]), 1)
        state = json.loads((self.profile / "zustand/installation.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "failed")
        self.assertTrue((self.home / "runtime/paket.json").exists())
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())

    def test_deep_runtime_parent_is_created_and_owned(self):
        self.config["paths"]["runtime"] = "~/new/parent/runtime"
        self.write_config()
        result = self.run_cli("--apply", answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / "new/parent/runtime/paket.json").is_file())
        state = json.loads((self.profile / "zustand/installation.json").read_text())
        self.assertIn(str(self.home / "new/parent"), state["created_directories"])

    def test_rule_fsync_failure_records_owned_partial_file(self):
        installer = self.load_installer()
        original = installer.sicher.os.fsync
        rule = self.home / ".claude/CLAUDE.md"
        def fail_once(fd):
            if rule.exists() and os.fstat(fd).st_ino == rule.stat().st_ino:
                raise OSError("synthetic fsync failure")
            return original(fd)
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer.sicher.os, "fsync", side_effect=fail_once):
            self.assertEqual(installer.main(["--config", str(self.config_path), "--home", str(self.home), "--apply"]), 1)
        state = json.loads((self.profile / "zustand/installation.json").read_text())
        self.assertEqual(state["status"], "failed")
        owned = next(item for item in state["created"] if item["path"] == str(rule))
        self.assertEqual(owned["inode"], rule.stat().st_ino)
        self.assertEqual(owned["sha256"], hashlib.sha256(rule.read_bytes()).hexdigest())
        self.assertTrue(owned["incomplete"])

    def test_replaced_journal_is_never_overwritten(self):
        installer = self.load_installer()
        actual_save = installer.Journal.save
        calls = 0
        foreign = b"foreign journal"
        def replace_before_save(journal, state):
            nonlocal calls
            calls += 1
            if calls == 2:
                path = self.profile / "zustand/installation.json"
                path.unlink()
                path.write_bytes(foreign)
            return actual_save(journal, state)
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer.Journal, "save", replace_before_save), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main(["--config", str(self.config_path), "--home", str(self.home), "--apply"]), 1)
        self.assertEqual((self.profile / "zustand/installation.json").read_bytes(), foreign)

    def test_temporary_symlink_parent_swap_cannot_write_outside(self):
        installer = self.load_installer()
        outside = self.root / "outside"
        outside.mkdir()
        (self.home / ".claude").mkdir()
        original_open = os.open
        swapped = False
        def swap_during_open(name, flags, *args, **kwargs):
            nonlocal swapped
            if name == ".claude" and kwargs.get("dir_fd") is not None and not swapped:
                swapped = True
                original = self.home / ".claude"
                parked = self.home / ".claude_parked"
                original.rename(parked)
                original.symlink_to(outside, target_is_directory=True)
                try:
                    return original_open(name, flags, *args, **kwargs)
                finally:
                    original.unlink()
                    parked.rename(original)
            return original_open(name, flags, *args, **kwargs)
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer.sicher.os, "open", side_effect=swap_during_open), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main(["--config", str(self.config_path), "--home", str(self.home), "--apply"]), 1)
        self.assertTrue(swapped)
        self.assertEqual(list(outside.iterdir()), [])

    def test_runtime_parent_swap_cannot_build_outside(self):
        self.config["paths"]["runtime"] = "~/holder/runtime"
        self.write_config()
        holder = self.home / "holder"
        holder.mkdir()
        outside = self.root / "outside_runtime"
        outside.mkdir()
        installer = self.load_installer()
        original_open = os.open
        swapped = False
        def swap_during_open(name, flags, *args, **kwargs):
            nonlocal swapped
            if name == "holder" and kwargs.get("dir_fd") is not None and not swapped:
                swapped = True
                parked = self.home / "holder_parked"
                holder.rename(parked)
                holder.symlink_to(outside, target_is_directory=True)
                try:
                    return original_open(name, flags, *args, **kwargs)
                finally:
                    holder.unlink()
                    parked.rename(holder)
            return original_open(name, flags, *args, **kwargs)
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer.sicher.os, "open", side_effect=swap_during_open), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main(["--config", str(self.config_path), "--home", str(self.home), "--apply"]), 1)
        self.assertTrue(swapped)
        self.assertEqual(list(outside.iterdir()), [])

    def test_moved_rule_parent_blocks_installed_status(self):
        installer = self.load_installer()
        original_write = installer.write_exclusive
        moved = False
        def move_after_write(path, data, created=None):
            nonlocal moved
            result = original_write(path, data, created=created)
            if Path(path).name == "CLAUDE.md" and not moved:
                moved = True
                parent = Path(path).parent
                parent.rename(parent.with_name(parent.name + "_moved"))
                parent.mkdir()
            return result
        with patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}), patch("builtins.input", return_value="yes"), patch.object(installer, "write_exclusive", side_effect=move_after_write), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main(["--config", str(self.config_path), "--home", str(self.home), "--apply"]), 1)
        self.assertTrue(moved)
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())
        self.assertTrue((self.home / ".claude_moved/CLAUDE.md").exists())
        state = json.loads((self.profile / "zustand/installation.json").read_text())
        self.assertEqual(state["status"], "failed")

    def test_absolute_package_key_rejected_before_staging(self):
        installer = self.load_installer()
        outside = self.root / "outside_marker"
        outside.write_bytes(b"unchanged")
        destination = self.home / "new_runtime"
        with self.assertRaises(OSError):
            installer.sicher.build_directory(destination, {outside: b"overwrite"})
        self.assertEqual(outside.read_bytes(), b"unchanged")
        self.assertFalse(destination.exists())
        self.assertFalse(any(self.home.glob(".aios-paket-*")))

    def test_moved_journal_parent_blocks_update(self):
        installer = self.load_installer()
        state_dir = self.profile / "zustand"
        state_dir.mkdir()
        path = state_dir / "installation.json"
        journal = installer.Journal(path, {"status": "installing"})
        try:
            moved = self.profile / "zustand_moved"
            state_dir.rename(moved)
            state_dir.mkdir()
            marker = state_dir / "installation.json"
            marker.write_bytes(b"foreign")
            with self.assertRaises(OSError):
                journal.save({"status": "installed"})
            self.assertEqual(marker.read_bytes(), b"foreign")
        finally:
            journal.close()

    def test_symlink_and_wrong_config_location_block(self):
        other = self.home / "other"
        other.mkdir()
        (self.home / "runtime").symlink_to(other, target_is_directory=True)
        result = self.run_cli("--apply", answer="yes\n")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.profile / "zustand").exists())
        (self.home / "runtime").unlink()
        copy = self.root / "copied.json"
        copy.write_bytes(self.config_path.read_bytes())
        result = subprocess.run([sys.executable, str(SCRIPT), "--config", str(copy), "--home", str(self.home)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.home / "runtime").exists())

    def test_config_file_name_of_other_language_reports_language_mismatch(self):
        self.config["language"] = "en"
        self.write_config()
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Configuration language en does not match the file name pfade.json", result.stderr)
        self.assertFalse((self.home / "runtime").exists())


if __name__ == "__main__":
    unittest.main()
