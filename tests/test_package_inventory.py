import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import test_package_operations as fixture

bestand = fixture.bestand
betrieb = fixture.betrieb


class OwnershipContractTests(unittest.TestCase):
    def setUp(self):
        self.case = fixture.PackageOperationTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.case.install()
        self.path = self.case.state_dir / "bestand.json"
        self.state = json.loads(self.path.read_bytes())

    def write_state(self, state):
        self.path.write_bytes(bestand.encoded(state))

    def test_manipulated_private_owned_path_stops_before_read(self):
        state = copy.deepcopy(self.state)
        marker = next(iter(self.case.markers))
        state["owned"][str(marker)] = {"role": "runtime_file", "sha256": "0" * 64}
        self.write_state(state)
        original = bestand.read_snapshot
        seen = []
        def guarded(path, limit=4 * 1024 * 1024):
            seen.append(Path(path))
            self.assertNotIn(Path(path), self.case.markers)
            return original(path, limit)
        with patch.object(bestand, "read_snapshot", side_effect=guarded):
            with self.assertRaises(bestand.BestandError):
                self.case.plan("uninstall")
        self.assertEqual(set(seen), {self.case.config_path, self.path})

    def test_private_manifest_roles_and_mac_aliases_rejected_before_read(self):
        for raw in ("allgemein/secrets/token.txt", "allgemein/credentials/token.txt", "allgemein/journals/private.json",
                    "allgemein/.env.example/secret.txt", "../profile/profil.md", "ALLGEMEIN/regeln/kern.md",
                    "allgemein/regeln/KERN.md"):
            with self.subTest(raw=raw):
                state = copy.deepcopy(self.state)
                state["manifest"]["files"].append({"path": raw, "sha256": "0" * 64})
                self.write_state(state)
                with self.assertRaises(bestand.BestandError):
                    self.case.plan("uninstall")
        for role in ("created_directory", "profile", "client_link"):
            with self.subTest(role=role):
                state = copy.deepcopy(self.state)
                path = next(path for path, item in state["owned"].items() if item["role"] == "runtime_file")
                state["owned"][path]["role"] = role
                self.write_state(state)
                with self.assertRaises(bestand.BestandError):
                    self.case.plan("uninstall")

    def test_bindings_cannot_target_private_root_home_overlap_or_symlink(self):
        outside = self.case.home / "alias"
        outside.symlink_to(self.case.profile, target_is_directory=True)
        for target in ("/", str(self.case.home), str(self.case.profile), str(self.case.home / "output"),
                       str(self.case.runtime), str(self.case.source), str(outside), str(self.case.home / ".claude")):
            with self.subTest(target=target):
                state = copy.deepcopy(self.state)
                state["bindings"]["codex"] = target
                self.write_state(state)
                with self.assertRaises((bestand.BestandError, ValueError, OSError)):
                    self.case.plan("uninstall")
        state = copy.deepcopy(self.state)
        state["bindings"]["codex_skills"] = str(self.case.home / "other-skills")
        self.write_state(state)
        with self.assertRaises(bestand.BestandError):
            self.case.plan()

    def test_race_immediately_before_mutation_does_not_overwrite(self):
        self.case.changed_source()
        planned = self.case.plan()
        original = betrieb.mutate
        victim = Path(next(step["path"] for step in planned["steps"] if step["kind"] == "replace"))
        fired = False
        def raced(step, data=None, **kwargs):
            nonlocal fired
            if not fired:
                fired = True
                victim.write_bytes(b"foreign changed during operation")
            return original(step, data, **kwargs)
        with patch.object(betrieb, "mutate", side_effect=raced):
            with self.assertRaises(bestand.BestandError):
                betrieb.execute(planned, self.case.config_path, self.case.home)
        self.assertEqual(victim.read_bytes(), b"foreign changed during operation")
        self.assertEqual(json.loads((self.case.state_dir / "operation.json").read_bytes())["status"], "interrupted")

    def test_lock_blocks_concurrent_command(self):
        planned = self.case.plan("uninstall")
        with bestand.operation_lock(self.case.state_dir):
            with self.assertRaises(bestand.BestandError):
                betrieb.execute(planned, self.case.config_path, self.case.home)
        self.assertFalse((self.case.state_dir / "operation.json").exists())

    def test_state_changed_after_preview_stops(self):
        planned = self.case.plan("uninstall")
        self.write_state(dict(self.state, status="uninstalled"))
        with self.assertRaises(bestand.BestandError):
            betrieb.execute(planned, self.case.config_path, self.case.home)
        self.assertTrue((self.case.runtime / "paket.json").is_file())

    def test_publication_failure_after_commit_still_reports_interrupted(self):
        self.case.changed_source()
        original = bestand.publish
        def fail_completion(path, value, previous=None):
            if Path(path).name == "operation.json" and value.get("status") == "completed":
                raise OSError("synthetic final journal failure")
            return original(path, value, previous)
        with patch.object(bestand, "publish", side_effect=fail_completion):
            with self.assertRaises(OSError):
                self.case.run_operation()
        self.assertNotEqual(json.loads(self.path.read_bytes())["manifest_sha256"], self.state["manifest_sha256"])
        self.assertEqual(fixture.einrichtungsstatus.inspect(self.case.config_path, self.case.home)["status"], "limited")
        with self.assertRaises(bestand.BestandError):
            self.case.plan()

    def test_created_directories_not_an_authority(self):
        legacy = self.case.state_dir / "installation.json"
        state = json.loads(legacy.read_bytes())
        state["created_directories"] += [str(self.case.home), str(self.case.profile), str(self.case.home / "output")]
        legacy.write_bytes(bestand.encoded(state))
        self.case.run_operation("uninstall")
        self.case.assert_private_unchanged()
        self.assertTrue(self.case.profile.is_dir())
        self.assertTrue((self.case.home / "output").is_dir())

    def test_manifest_extension_cannot_claim_foreign_runtime_file(self):
        marker = self.case.runtime / "allgemein/skills/alpha/foreign.txt"
        marker.write_bytes(b"FOREIGN_RUNTIME_MARKER")
        state = copy.deepcopy(self.state)
        sha = bestand.digest(marker.read_bytes())
        state["manifest"]["files"].append({"path": "allgemein/skills/alpha/foreign.txt", "sha256": sha})
        state["owned"][str(marker)] = {"role": "runtime_file", "sha256": sha}
        self.write_state(state)
        original = bestand.read_snapshot
        def guarded(path, limit=4 * 1024 * 1024):
            self.assertNotEqual(Path(path), marker, "Foreign file read from manipulated inventory")
            return original(path, limit)
        with patch.object(bestand, "read_snapshot", side_effect=guarded):
            result = fixture.einrichtungsstatus.inspect(self.case.config_path, self.case.home)
            self.assertEqual(result["status"], "limited")
            with self.assertRaises(bestand.BestandError):
                self.case.plan("uninstall")
        self.assertEqual(marker.read_bytes(), b"FOREIGN_RUNTIME_MARKER")
        self.assertFalse((self.case.state_dir / "operation.json").exists())

    def test_keep_edit_stops_before_first_file_mutation(self):
        self.case.changed_source()
        planned = self.case.plan()
        victim = Path(next(step["path"] for step in planned["steps"]
                           if step["kind"] == "keep" and step["before"]["role"] == "runtime_file"))
        before = {path: bestand.check_target(path, item) for path, item in planned["old"]["owned"].items()}
        original = betrieb.mutate
        count = 0
        def raced(step, data=None, **kwargs):
            nonlocal count
            count += 1
            victim.write_bytes(b"LOCAL KEEP EDIT")
            return original(step, data, **kwargs)
        with patch.object(betrieb, "mutate", side_effect=raced):
            with self.assertRaises(bestand.BestandError):
                betrieb.execute(planned, self.case.config_path, self.case.home)
        self.assertEqual(count, 1)
        for path, item in planned["old"]["owned"].items():
            if Path(path) != victim:
                self.assertEqual(bestand.check_target(path, item), before[path])
        self.assertFalse(list(self.case.home.rglob(".aios-aufnahme-*")))
        operation = json.loads((self.case.state_dir / "operation.json").read_bytes())
        self.assertEqual(operation["status"], "interrupted")
        self.assertNotIn("done", {step["status"] for step in operation["steps"]})

    def test_foreign_link_swapped_at_capture_is_restored_and_operation_stops(self):
        victim = self.case.home / ".agents/skills/alpha"
        original = betrieb.sicher.exclusive_move_at
        fired = False
        def raced(source_fd, source_name, target_fd, target_name):
            nonlocal fired
            if not fired and source_name == "alpha" and target_name == "object":
                fired = True
                os.unlink(source_name, dir_fd=source_fd)
                os.symlink(self.case.home / "output", source_name, dir_fd=source_fd)
            return original(source_fd, source_name, target_fd, target_name)
        with patch.object(betrieb.sicher, "exclusive_move_at", side_effect=raced):
            with self.assertRaises(bestand.BestandError):
                self.case.run_operation("uninstall")
        self.assertTrue(fired)
        self.assertEqual(os.readlink(victim), str(self.case.home / "output"))
        operation = json.loads((self.case.state_dir / "operation.json").read_bytes())
        self.assertEqual(operation["status"], "interrupted")
        self.assertIn("foreign_restored", {step.get("capture", {}).get("status") for step in operation["steps"]})

    def test_foreign_file_swapped_at_capture_is_restored_without_read(self):
        self.case.changed_source()
        victim = self.case.runtime / "allgemein/regeln/kern.md"
        original = betrieb.sicher.exclusive_move_at
        original_read = os.read
        foreign_inode = None
        fired = False
        def raced(source_fd, source_name, target_fd, target_name):
            nonlocal fired, foreign_inode
            if not fired and source_name == "kern.md" and target_name == "object":
                fired = True
                os.unlink(source_name, dir_fd=source_fd)
                victim.write_bytes(b"FOREIGN REPLACEMENT")
                foreign_inode = victim.stat().st_ino
            return original(source_fd, source_name, target_fd, target_name)
        def guarded(fd, size):
            self.assertNotEqual(os.fstat(fd).st_ino, foreign_inode)
            return original_read(fd, size)
        with patch.object(betrieb.sicher, "exclusive_move_at", side_effect=raced), patch.object(os, "read", side_effect=guarded):
            with self.assertRaises(bestand.BestandError):
                self.case.run_operation()
        self.assertTrue(fired)
        self.assertEqual(victim.read_bytes(), b"FOREIGN REPLACEMENT")
        self.assertEqual(json.loads((self.case.state_dir / "operation.json").read_bytes())["status"], "interrupted")

    def test_foreign_capture_kept_when_restore_target_is_occupied(self):
        victim = self.case.home / ".agents/skills/alpha"
        original = betrieb.sicher.exclusive_move_at
        fired = False
        def raced(source_fd, source_name, target_fd, target_name):
            nonlocal fired
            selected = not fired and source_name == "alpha" and target_name == "object"
            if selected:
                fired = True
                os.unlink(source_name, dir_fd=source_fd)
                os.symlink(self.case.home / "output", source_name, dir_fd=source_fd)
            result = original(source_fd, source_name, target_fd, target_name)
            if selected:
                os.symlink(self.case.profile, source_name, dir_fd=source_fd)
            return result
        with patch.object(betrieb.sicher, "exclusive_move_at", side_effect=raced):
            with self.assertRaises(bestand.BestandError):
                self.case.run_operation("uninstall")
        self.assertEqual(os.readlink(victim), str(self.case.profile))
        operation = json.loads((self.case.state_dir / "operation.json").read_bytes())
        captures = [step["capture"] for step in operation["steps"] if step.get("capture", {}).get("status") == "foreign_retained"]
        self.assertEqual(len(captures), 1)
        self.assertEqual(os.readlink(captures[0]["object"]), str(self.case.home / "output"))
        self.assertEqual(Path(captures[0]["directory"]).stat().st_mode & 0o777, 0o700)
        self.assertEqual(operation["status"], "interrupted")

    def test_foreign_metadata_at_exchange_survives_and_status_is_interrupted(self):
        self.case.changed_source()
        original = betrieb.sicher.exchange_at
        fired = False
        def raced(parent_fd, first, second):
            nonlocal fired
            if not fired and second == "bestand.json":
                fired = True
                os.unlink(second, dir_fd=parent_fd)
                self.path.write_bytes(b"FOREIGN METADATA")
            return original(parent_fd, first, second)
        with patch.object(betrieb.sicher, "exchange_at", side_effect=raced):
            with self.assertRaises(bestand.BestandError):
                self.case.run_operation()
        self.assertTrue(fired)
        self.assertIn(b"FOREIGN METADATA", [path.read_bytes() for path in self.case.state_dir.glob(".aios-bestand-*")])
        self.assertEqual(fixture.einrichtungsstatus.inspect(self.case.config_path, self.case.home)["status"], "limited")
        with self.assertRaises(bestand.BestandError):
            self.case.plan()

    def test_failure_after_completed_journal_publication_remains_interrupted(self):
        self.case.changed_source()
        original = bestand.publish
        def fail_after_completion(path, value, previous=None):
            result = original(path, value, previous)
            if Path(path).name == "operation.json" and value.get("status") == "completed":
                raise OSError("synthetic failure after completed publication")
            return result
        with patch.object(bestand, "publish", side_effect=fail_after_completion):
            with self.assertRaises(OSError):
                self.case.run_operation()
        operation = json.loads((self.case.state_dir / "operation.json").read_bytes())
        self.assertEqual(operation["status"], "interrupted")
        self.assertEqual(fixture.einrichtungsstatus.inspect(self.case.config_path, self.case.home)["status"], "limited")
        with self.assertRaises(bestand.BestandError):
            self.case.plan()


if __name__ == "__main__":
    unittest.main()
