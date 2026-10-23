import contextlib
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


PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "scripts"))
import setup as aios_setup


class SetupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=PACKAGE.parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.codex = self.root / "codex custom"
        self.claude = self.root / "claude custom"

    def run_setup(self, profile="yes", install="yes", extra=(), env_override=None, language="de"):
        answers = [language, "both", "", "", "", "", "", "", *([""] * 7), profile]
        if profile == "yes":
            answers += ["no", install]
        env = os.environ.copy()
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        if env_override:
            env.update(env_override)
        return subprocess.run(["/bin/sh", str(PACKAGE / "install.sh"), "--home", str(self.home),
                               "--codex-home", str(self.codex), "--claude-config-dir", str(self.claude),
                               *extra], input="\n".join(answers) + "\n", text=True,
                              capture_output=True, env=env)

    def test_shell_guided_happy_path_and_status(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preview of the local configuration", result.stdout)
        self.assertIn("Read-only status check", result.stdout)
        self.assertIn("File integration: present", result.stdout)
        self.assertFalse(any(ch in result.stdout + result.stderr for ch in "äöüÄÖÜß"))
        config = json.loads((self.home / "aios-profile/pfade.json").read_text())
        self.assertTrue(config["confirmed"])
        self.assertEqual(json.loads((self.home / "aios-profile/zustand/installation.json").read_text())["status"], "installed")
        self.assertTrue((self.codex / "AGENTS.md").is_file())
        self.assertTrue((self.claude / "CLAUDE.md").is_file())

    def test_profile_cancel_writes_nothing(self):
        result = self.run_setup(profile="no")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_install_cancel_keeps_profile_and_quotes_resume(self):
        result = self.run_setup(install="no")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.home / "aios-profile/pfade.json"
        self.assertTrue(config.is_file())
        self.assertFalse((self.home / "aios-runtime").exists())
        resume = result.stdout.split("Continue the installation with:\n", 1)[1].splitlines()[0]
        self.assertEqual(shlex.split(resume), ["sh", str(PACKAGE / "install.sh"),
                         "--config", str(config), "--home", str(self.home),
                         "--codex-home", str(self.codex), "--claude-config-dir", str(self.claude), "--apply"])

    def test_install_conflict_stops_after_profile(self):
        self.codex.mkdir()
        marker = self.codex / "AGENTS.md"
        marker.write_text("foreign")
        result = self.run_setup()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Pre-installation plan contains conflicts", result.stderr)
        self.assertEqual(marker.read_text(), "foreign")
        self.assertFalse((self.home / "aios-runtime").exists())
        self.assertTrue((self.home / "aios-profile/pfade.json").is_file())

    def test_interrupt_at_install_confirmation_keeps_profile_and_resume(self):
        answers = iter(["de", "both", "", "", "", "", "", "", *([""] * 7), "yes", "no"])
        def answer(prompt):
            if "Run the first installation?" in prompt:
                raise KeyboardInterrupt
            return next(answers)
        output, errors = io.StringIO(), io.StringIO()
        with patch("builtins.input", side_effect=answer), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            result = aios_setup.main(["--home", str(self.home), "--codex-home", str(self.codex),
                                      "--claude-config-dir", str(self.claude)])
        self.assertEqual(result, 0, errors.getvalue())
        self.assertTrue((self.home / "aios-profile/pfade.json").is_file())
        self.assertFalse((self.home / "aios-profile/zustand").exists())
        self.assertFalse((self.home / "aios-runtime").exists())
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.claude.exists())
        resume = output.getvalue().split("Continue the installation with:\n", 1)[1].splitlines()[0]
        self.assertEqual(shlex.split(resume), ["sh", str(PACKAGE / "install.sh"),
                         "--config", str(self.home / "aios-profile/pfade.json"), "--home", str(self.home),
                         "--codex-home", str(self.codex), "--claude-config-dir", str(self.claude), "--apply"])
        self.assertNotIn("Traceback", errors.getvalue())

    def test_missing_binaries_are_reported_without_blocking(self):
        binary_dir = self.root / "bin"
        binary_dir.mkdir()
        (binary_dir / "python3").symlink_to(sys.executable)
        result = self.run_setup(env_override={"PATH": str(binary_dir)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("claude is not available in PATH", result.stdout)
        self.assertIn("codex is not available in PATH", result.stdout)
        self.assertIn("File integration: present", result.stdout)

    def test_config_keeps_preview_default_and_help_has_no_effect(self):
        result = subprocess.run(["sh", str(PACKAGE / "install.sh"), "--home", str(self.home), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--config", result.stdout)
        self.assertEqual(list(self.home.iterdir()), [])
        self.run_setup(install="no")
        config = self.home / "aios-profile/pfade.json"
        result = subprocess.run(["sh", str(PACKAGE / "install.sh"), "--config", str(config),
                                 "--home", str(self.home), "--codex-home", str(self.codex),
                                 "--claude-config-dir", str(self.claude)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preview. No files or folders created.", result.stdout)
        self.assertFalse((self.home / "aios-runtime").exists())

    def test_language_option_with_config_is_rejected(self):
        result = subprocess.run(["sh", str(PACKAGE / "install.sh"), "--config", str(self.root / "paths.json"),
                                 "--home", str(self.home), "--language", "en"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--language only applies to a new profile", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_english_cancel_after_language_choice_writes_nothing(self):
        result = self.run_setup(profile="no", language="")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"language": "en"', result.stdout)
        self.assertIn("paths.json, profile.md, projects.md, knowledge/INDEX.md and .env", result.stdout)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
