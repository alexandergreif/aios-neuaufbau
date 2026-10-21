import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPTS = PACKAGE / "scripts"


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=PACKAGE.parent)
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.home.mkdir()
        self.profile = self.home / "profile"
        self.profile.mkdir()
        self.config_path = self.profile / "pfade.json"
        self.config_path.write_text(json.dumps({
            "schema_version": 1, "confirmed": True, "clients": ["claude-code", "codex"],
            "paths": {"source": str(PACKAGE), "runtime": "~/runtime", "profile": "~/profile",
                      "output": "~/output", "coding_roots": [], "customer_roots": []},
        }), encoding="utf-8")
        (self.profile / "profil.md").write_bytes(b"synthetic private")
        (self.profile / ".env").write_bytes(b"SECRET=synthetic")
        env = os.environ.copy()
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        self.env = env
        installed = subprocess.run([sys.executable, str(SCRIPTS / "installieren.py"), "--config", str(self.config_path),
                                    "--home", str(self.home), "--apply"], input="ja\n", text=True,
                                   capture_output=True, env=env)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.runtime = self.home / "runtime"
        self.state_path = self.profile / "zustand/installation.json"
        # Diese bestehende Matrix prüft ausdrücklich den weiterhin lesbaren v1-Vertrag.
        (self.profile / "zustand/bestand.json").unlink()

    def run_status(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPTS / "einrichtungsstatus.py"), "--config", str(self.config_path),
                               "--home", str(self.home), "--json", *map(str, extra)],
                              capture_output=True, text=True, env=self.env, timeout=5)

    def load_status(self):
        with patch.object(sys, "path", [str(SCRIPTS), *sys.path]):
            spec = importlib.util.spec_from_file_location("status_test", SCRIPTS / "einrichtungsstatus.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    def state(self):
        return json.loads(self.state_path.read_text())

    def write_state(self, value):
        self.state_path.write_text(json.dumps(value), encoding="utf-8")

    def test_intact_status_is_only_file_integrity(self):
        before = {p: p.read_bytes() for p in (self.config_path, self.profile / "profil.md", self.profile / ".env", self.runtime / "paket.json")}
        result = self.run_status()
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value["status"], "vorhanden")
        self.assertEqual(value["fachfunktion"], "ungeprüft")
        self.assertEqual({x["client"] for x in value["clients"]}, {"claude-code", "codex"})
        self.assertTrue(all(x["skills"] > 0 and x["modell_dienste"] == "ungeprüft" for x in value["clients"]))
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_modified_package_hash_and_missing_file(self):
        target = self.runtime / "allgemein/regeln/kern.md"
        target.write_bytes(target.read_bytes() + b"changed")
        self.assertEqual(self.run_status().returncode, 1)
        target.unlink()
        self.assertEqual(json.loads(self.run_status().stdout)["status"], "fehlend")

    def test_missing_and_redirected_link(self):
        link = next((self.home / ".claude/skills").iterdir())
        link.unlink()
        missing = json.loads(self.run_status().stdout)
        self.assertEqual(missing["status"], "fehlend")
        by_client = {item["client"]: item for item in missing["clients"]}
        self.assertEqual(by_client["claude-code"]["status"], "fehlend")
        self.assertEqual(by_client["codex"]["status"], "vorhanden")
        self.assertGreater(by_client["codex"]["skills"], 0)
        self.assertIn(link.name, " ".join(missing["probleme"]))
        link.symlink_to(self.home / "output", target_is_directory=True)
        self.assertEqual(json.loads(self.run_status().stdout)["status"], "eingeschränkt")

    def test_moved_client_directories_do_not_mask_other_client(self):
        claude = self.home / ".claude"
        claude.rename(self.home / ".claude-moved")
        value = json.loads(self.run_status().stdout)
        clients = {item["client"]: item for item in value["clients"]}
        self.assertEqual(clients["claude-code"]["status"], "fehlend")
        self.assertEqual(clients["codex"]["status"], "vorhanden")
        self.assertGreater(clients["codex"]["skills"], 0)
        (self.home / ".claude-moved").rename(claude)
        codex_skills = self.home / ".agents/skills"
        codex_skills.rename(self.home / ".agents/skills-moved")
        value = json.loads(self.run_status().stdout)
        clients = {item["client"]: item for item in value["clients"]}
        self.assertEqual(clients["codex"]["status"], "fehlend")
        self.assertEqual(clients["claude-code"]["status"], "vorhanden")
        self.assertGreater(clients["claude-code"]["skills"], 0)

    def test_bundled_status_runs_without_source_imports(self):
        script = self.runtime / "scripts/einrichtungsstatus.py"
        helper = self.runtime / "scripts/sichere_dateien.py"
        policy = self.runtime / "scripts/paketregeln.py"
        self.assertTrue(script.is_file())
        self.assertTrue(helper.is_file())
        self.assertTrue(policy.is_file())
        isolated = Path(self.temp.name) / "isolated"
        isolated.mkdir()
        env = dict(self.env)
        env.pop("PYTHONPATH", None)
        def run():
            return subprocess.run([sys.executable, str(script), "--config", str(self.config_path),
                                   "--home", str(self.home), "--json"], cwd=isolated,
                                  capture_output=True, text=True, env=env, timeout=5)
        intact = run()
        self.assertEqual(intact.returncode, 0, intact.stderr)
        self.assertEqual(json.loads(intact.stdout)["status"], "vorhanden")
        link = next((self.home / ".claude/skills").iterdir())
        link.unlink()
        link.symlink_to(self.home / "output", target_is_directory=True)
        broken = run()
        self.assertEqual(broken.returncode, 1, broken.stderr)
        clients = {item["client"]: item for item in json.loads(broken.stdout)["clients"]}
        self.assertEqual(clients["claude-code"]["status"], "eingeschränkt")
        self.assertEqual(clients["codex"]["status"], "vorhanden")

    def test_fifo_package_file_does_not_block(self):
        target = self.runtime / "allgemein/regeln/kern.md"
        target.unlink()
        os.mkfifo(target)
        result = self.run_status()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "eingeschränkt")

    def test_leaf_replacement_during_read_is_detected(self):
        status = self.load_status()
        target = self.runtime / "allgemein/regeln/kern.md"
        replacement = target.with_name("replacement.md")
        replacement.write_bytes(b"foreign replacement")
        original_read = os.read
        original_inode = target.stat().st_ino
        changed = False
        def replace_on_read(fd, size):
            nonlocal changed
            if not changed and os.fstat(fd).st_ino == original_inode:
                changed = True
                target.unlink()
                replacement.rename(target)
            return original_read(fd, size)
        with patch.object(status.os, "read", side_effect=replace_on_read):
            with self.assertRaises(status.StatusError):
                status.read_file(target)
        self.assertTrue(changed)

    def test_wrong_state_path_and_incomplete_states(self):
        state = self.state()
        state["created"].append({"type": "file", "path": str(self.home / "output/private.txt"), "sha256": "0" * 64})
        self.write_state(state)
        self.assertEqual(self.run_status().returncode, 1)
        state["created"].pop()
        for status in ("installing", "failed"):
            state["status"] = status
            self.write_state(state)
            self.assertEqual(json.loads(self.run_status().stdout)["status"], "eingeschränkt")

    def test_manifest_traversal_rejected_before_outside_read(self):
        manifest_path = self.runtime / "paket.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"].append({"path": "../outside_marker", "sha256": "0" * 64})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        status = self.load_status()
        actual_read = status.read_file
        seen = []
        def record(path, limit=None):
            seen.append(Path(path))
            return actual_read(path, limit)
        with patch.object(status, "read_file", side_effect=record):
            result = status.inspect(self.config_path, self.home)
        self.assertEqual(result["status"], "eingeschränkt")
        self.assertEqual(seen, [self.config_path, manifest_path])

    def test_consistent_private_manifest_and_journal_still_blocked(self):
        marker = self.runtime / ".env"
        marker.write_bytes(b"PRIVATE=synthetic")
        manifest_path = self.runtime / "paket.json"
        manifest = json.loads(manifest_path.read_text())
        import hashlib
        manifest["files"].append({"path": ".env", "sha256": hashlib.sha256(marker.read_bytes()).hexdigest()})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        state = self.state()
        state["created"].append({"type": "file", "path": str(marker), "sha256": manifest["files"][-1]["sha256"]})
        self.write_state(state)
        status = self.load_status()
        actual_read = status.read_file
        seen = []
        def record(path, limit=None):
            seen.append(Path(path))
            return actual_read(path, limit)
        with patch.object(status, "read_file", side_effect=record):
            result = status.inspect(self.config_path, self.home)
        self.assertEqual(result["status"], "eingeschränkt")
        self.assertNotIn(marker, seen)

    def test_private_subdirectories_rejected_before_content_read(self):
        import hashlib
        status = self.load_status()
        actual_read = status.read_file
        manifest_path = self.runtime / "paket.json"
        original_manifest = manifest_path.read_bytes()
        original_state = self.state()
        for relative in ("allgemein/secrets/token.txt", "allgemein/credentials/token.txt",
                         "allgemein/journals/action.json"):
            with self.subTest(relative=relative):
                marker = self.runtime / relative
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.write_bytes(b"SYNTHETIC_PRIVATE_MARKER")
                manifest = json.loads(original_manifest)
                digest = hashlib.sha256(marker.read_bytes()).hexdigest()
                manifest["files"].append({"path": relative, "sha256": digest})
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                state = json.loads(json.dumps(original_state))
                state["created"].append({"type": "file", "path": str(marker), "sha256": digest})
                self.write_state(state)
                seen = []
                def record(path, limit=None):
                    seen.append(Path(path))
                    return actual_read(path, limit)
                with patch.object(status, "read_file", side_effect=record):
                    result = status.inspect(self.config_path, self.home)
                self.assertEqual(result["status"], "eingeschränkt")
                self.assertNotIn(marker, seen)
                manifest_path.write_bytes(original_manifest)
                self.write_state(original_state)
                marker.unlink()
                marker.parent.rmdir()

    def test_nul_manifest_path_is_handled_without_traceback(self):
        manifest_path = self.runtime / "paket.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"].append({"path": "allgemein/evil\x00.md", "sha256": "0" * 64})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.run_status()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)

    def test_manifest_duplicate_and_symlink_rejected(self):
        manifest_path = self.runtime / "paket.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"].append(dict(manifest["files"][0]))
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(self.run_status().returncode, 1)
        manifest["files"].pop()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        target = self.runtime / manifest["files"][0]["path"]
        target.unlink()
        target.symlink_to(self.profile / "profil.md")
        self.assertEqual(self.run_status().returncode, 1)

    def test_missing_runtime_and_state(self):
        self.state_path.unlink()
        self.assertEqual(json.loads(self.run_status().stdout)["status"], "fehlend")
        (self.runtime / "paket.json").unlink()
        self.assertEqual(json.loads(self.run_status().stdout)["status"], "fehlend")

    def test_existing_output_marker_unchanged(self):
        marker = self.home / "output/marker.txt"
        marker.write_bytes(b"untouched")
        self.assertEqual(self.run_status().returncode, 0)
        self.assertEqual(marker.read_bytes(), b"untouched")


if __name__ == "__main__":
    unittest.main()
