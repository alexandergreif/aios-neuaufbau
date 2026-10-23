"""English package lifecycle with synthetic sources, profile and client folders only."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "scripts"))
import build_package
import install
import package_inventory as bestand
import package_operations as operations
import package_rules
import setup_status


class EnglishLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=PACKAGE.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.source = self.root / "source"
        (self.source / "scripts").mkdir(parents=True)
        for name in package_rules.SCRIPT_NAMES:
            (self.source / "scripts" / name).write_bytes((PACKAGE / "scripts" / name).read_bytes())
        self.put_source("en/rules/core.md", b"# Synthetic core\n\nSee [storage](../references/storage.md).\n")
        self.put_source("en/references/storage.md", b"# Storage\n")
        self.put_source("en/skills/alpha/SKILL.md", b"alpha")
        self.put_source("en/skills/alpha/old.txt", b"old")
        self.put_source("en/templates/profile.md", b"# Personal profile\n")
        self.profile = self.home / "profile"
        self.profile.mkdir()
        self.config_path = self.profile / "paths.json"
        self.config = {"schema_version": 1, "confirmed": True, "language": "en", "clients": ["claude-code", "codex"],
                       "paths": {"source": str(self.source), "runtime": "~/runtime", "profile": "~/profile",
                                 "output": "~/output", "coding_roots": [], "customer_roots": []}}
        self.config_path.write_bytes(bestand.encoded(self.config))
        self.markers = {}
        for path in (self.profile / "profile.md", self.profile / ".env", self.profile / "knowledge/note.md",
                     self.home / "output/result.txt"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"SYNTHETIC_PRIVATE_MARKER")
            self.markers[path] = path.read_bytes()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(build_package, "PACKAGE", self.source))
        self.stack.enter_context(patch.dict(os.environ, {"CODEX_HOME": "", "CLAUDE_CONFIG_DIR": ""}))
        self.state_dir = self.profile / "state"
        self.runtime = self.home / "runtime"

    def put_source(self, relative, value):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)

    def install(self):
        args = ["--config", str(self.config_path), "--home", str(self.home), "--apply"]
        with patch("builtins.input", return_value="yes"), redirect_stdout(io.StringIO()) as output, \
                redirect_stderr(io.StringIO()) as errors:
            result = install.main(args)
        self.assertEqual(result, 0, errors.getvalue())
        return output.getvalue()

    def test_install_status_update_uninstall(self):
        output = self.install()
        self.assertIn("Language of rules and skills: en", output)
        self.assertFalse((self.profile / "zustand").exists())
        self.assertTrue((self.state_dir / "installation.json").is_file())
        self.assertTrue((self.state_dir / "bestand.json").is_file())
        manifest = json.loads((self.runtime / "paket.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["language"], "en")
        self.assertEqual(manifest["version"], build_package.VERSION)
        self.assertTrue((self.runtime / "general/rules/core.md").is_file())
        self.assertFalse((self.runtime / "allgemein").exists())
        self.assertTrue((self.runtime / "scripts/languages.py").is_file())
        config_link = quote(str(self.config_path), safe="/")
        profile_link = quote(str(self.profile / "profile.md"), safe="/")
        reference = quote(str(self.runtime / "general/references/storage.md"), safe="/")
        for rule in (self.home / ".claude/CLAUDE.md", self.home / ".codex/AGENTS.md"):
            text = rule.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("<!-- Generated from general/rules/core.md. SHA256: "), text[:80])
            self.assertIn(f"Local configuration: [paths.json](<{config_link}>)", text)
            self.assertIn(f"Profile: [profile.md](<{profile_link}>)", text)
            self.assertIn(f"[storage](<{reference}>)", text)
            self.assertNotIn("(../references/", text)
            self.assertNotIn("Profil:", text)
        for link in (self.home / ".claude/skills/alpha", self.home / ".agents/skills/alpha"):
            self.assertEqual(os.readlink(link), str(self.runtime / "general/skills/alpha"))

        status = setup_status.inspect(self.config_path, self.home)
        self.assertEqual(status["status"], "present")
        self.assertEqual(status["language"], "en")
        self.assertEqual({item["client"]: item["skills"] for item in status["clients"]}, {"claude-code": 1, "codex": 1})
        bundled = subprocess.run([sys.executable, str(self.runtime / "scripts/setup_status.py"),
                                  "--config", str(self.config_path), "--home", str(self.home), "--json"],
                                 cwd=self.root, capture_output=True, text=True, timeout=10,
                                 env={k: v for k, v in os.environ.items() if k not in ("CODEX_HOME", "CLAUDE_CONFIG_DIR")})
        self.assertEqual(bundled.returncode, 0, bundled.stderr)
        self.assertEqual(json.loads(bundled.stdout)["status"], "present")

        self.put_source("en/rules/core.md", b"# Changed synthetic core\n")
        (self.source / "en/skills/alpha/old.txt").unlink()
        self.put_source("en/skills/beta/SKILL.md", b"beta")
        planned = operations.plan("update", self.config_path, self.home)
        self.assertEqual({step["kind"] for step in planned["steps"]}, {"add", "replace", "remove", "keep"})
        operations.execute(planned, self.config_path, self.home)
        self.assertEqual(setup_status.inspect(self.config_path, self.home)["status"], "present")
        rule = (self.home / ".codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("# Changed synthetic core", rule)
        self.assertIn(f"Profile: [profile.md](<{profile_link}>)", rule)
        self.assertEqual(os.readlink(self.home / ".agents/skills/beta"), str(self.runtime / "general/skills/beta"))
        self.assertEqual(len(list((self.state_dir / "sicherungen").glob("*/*.md"))), 2)

        with redirect_stdout(io.StringIO()) as preview:
            self.assertEqual(operations.main("uninstall", ["--config", str(self.config_path), "--home", str(self.home)]), 0)
        self.assertIn("(en)", preview.getvalue())
        operations.execute(operations.plan("uninstall", self.config_path, self.home), self.config_path, self.home)
        self.assertEqual(setup_status.inspect(self.config_path, self.home)["status"], "uninstalled")
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())
        self.assertFalse((self.home / ".agents/skills/alpha").exists())
        for path, value in self.markers.items():
            self.assertEqual(path.read_bytes(), value)

    def test_language_change_is_not_an_update(self):
        self.install()
        state = json.loads((self.state_dir / "bestand.json").read_bytes())
        german = dict(self.config, language="de")
        with self.assertRaises(bestand.BestandError):
            bestand.validate(state, german, self.home)
        without_field = {key: value for key, value in self.config.items() if key != "language"}
        with self.assertRaises(bestand.BestandError):
            bestand.validate(state, without_field, self.home)
        self.config_path.write_bytes(bestand.encoded(german))
        with self.assertRaises(bestand.BestandError):
            operations.plan("update", self.config_path, self.home)

    def test_config_name_must_match_language(self):
        wrong = self.profile / "pfade.json"
        wrong.write_bytes(self.config_path.read_bytes())
        with patch("builtins.input", return_value="yes"), redirect_stdout(io.StringIO()), \
                redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(install.main(["--config", str(wrong), "--home", str(self.home), "--apply"]), 1)
        self.assertIn("Configuration language en does not match the file name pfade.json", errors.getvalue())
        self.assertFalse(self.runtime.exists())
        self.assertFalse(self.state_dir.exists())
    def test_config_file_name_of_other_language_reports_language_mismatch(self):
        self.install()
        german_name = self.profile / "pfade.json"
        german_name.write_bytes(self.config_path.read_bytes())
        with self.assertRaisesRegex(bestand.BestandError, "language en does not match the file name pfade.json"):
            operations.plan("update", german_name, self.home)
        with self.assertRaisesRegex(setup_status.StatusError, "language en does not match"):
            setup_status.inspect(german_name, self.home)
        without_field = {key: value for key, value in self.config.items() if key != "language"}
        self.config_path.write_bytes(bestand.encoded(without_field))
        with self.assertRaisesRegex(bestand.BestandError, "language de does not match the file name paths.json"):
            operations.plan("update", self.config_path, self.home)
        with redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(operations.main("uninstall", ["--config", str(self.config_path), "--home", str(self.home)]), 1)
        self.assertIn('keep paths.json with "language": "en"', errors.getvalue())

    def test_legacy_script_names_only_in_manifests_without_language(self):
        self.install()
        manifest = json.loads((self.runtime / "paket.json").read_text(encoding="utf-8"))
        legacy = {"path": "scripts/einrichten.py", "sha256": "0" * 64}
        tagged = dict(manifest, files=[*manifest["files"], legacy])
        with self.assertRaises(bestand.BestandError):
            bestand.manifest_entries(tagged)
        with self.assertRaises(setup_status.StatusError):
            setup_status.manifest_entries(tagged)
        files = [{"path": "allgemein/regeln/kern.md", "sha256": "1" * 64},
                 {"path": "allgemein/skills/alpha/SKILL.md", "sha256": "2" * 64}, legacy]
        german = {"schema_version": 1, "version": "0.2.0-dev", "language": "de", "files": files}
        with self.assertRaises(bestand.BestandError):
            bestand.manifest_entries(german)
        with self.assertRaises(setup_status.StatusError):
            setup_status.manifest_entries(german)
        untagged = {key: value for key, value in german.items() if key != "language"}
        self.assertIn("scripts/einrichten.py", bestand.manifest_entries(untagged))
        self.assertIn("scripts/einrichten.py", setup_status.manifest_entries(untagged))


class EnglishGuidedSetupTests(unittest.TestCase):
    """End-to-end guided setup with the real English tree in a synthetic home."""

    def setUp(self):
        if not (PACKAGE / "en/rules/core.md").is_file() or not any((PACKAGE / "en/skills").glob("*/SKILL.md")):
            self.skipTest("English package content not present")
        temporary = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=PACKAGE.parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.codex = self.root / "codex custom"
        self.claude = self.root / "claude custom"

    def test_default_language_installs_english_package(self):
        answers = ["", "both", "", "", "", "", "", "", *([""] * 7), "yes", "no", "yes"]
        env = os.environ.copy()
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        result = subprocess.run(["/bin/sh", str(PACKAGE / "install.sh"), "--home", str(self.home),
                                 "--codex-home", str(self.codex), "--claude-config-dir", str(self.claude)],
                                input="\n".join(answers) + "\n", text=True, capture_output=True, env=env, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("File integration: present", result.stdout)
        self.assertFalse(any(ch in result.stdout + result.stderr for ch in "äöüÄÖÜß"))
        profile = self.home / "aios-profile"
        self.assertEqual(sorted(p.name for p in profile.iterdir()),
                         [".env", "knowledge", "paths.json", "profile.md", "projects.md", "state"])
        self.assertEqual(json.loads((profile / "paths.json").read_text())["language"], "en")
        runtime = self.home / "aios-runtime"
        self.assertEqual(json.loads((runtime / "paket.json").read_text())["language"], "en")
        self.assertEqual(os.readlink(self.claude / "skills/prepare-brief"), str(runtime / "general/skills/prepare-brief"))
        self.assertFalse((self.claude / "skills/auftrag-vorbereiten").exists())
        rule = (self.codex / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(rule.startswith("<!-- Generated from general/rules/core.md. SHA256: "))
        self.assertIn("Profile: [profile.md](<", rule)
        status = subprocess.run([sys.executable, str(runtime / "scripts/setup_status.py"), "--config",
                                 str(profile / "paths.json"), "--home", str(self.home), "--codex-home", str(self.codex),
                                 "--claude-config-dir", str(self.claude), "--json"],
                                capture_output=True, text=True, env=env, timeout=10)
        self.assertEqual(status.returncode, 0, status.stderr)
        value = json.loads(status.stdout)
        self.assertEqual(value["status"], "present")
        self.assertTrue(all(item["skills"] == 21 for item in value["clients"]))


if __name__ == "__main__":
    unittest.main()
