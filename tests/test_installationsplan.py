import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / "scripts/installationsplan.py"


class InstallationPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=PACKAGE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.config_path = self.root / "pfade.json"
        self.config = {
            "schema_version": 1,
            "confirmed": True,
            "clients": ["claude-code", "codex"],
            "paths": {"source": "~/source", "runtime": "~/runtime", "profile": "~/profile",
                      "output": "~/output", "coding_roots": [], "customer_roots": []},
        }

    def run_plan(self, *extra, env=None):
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        process_env = os.environ.copy()
        process_env.pop("CODEX_HOME", None)
        process_env.pop("CLAUDE_CONFIG_DIR", None)
        if env:
            process_env.update(env)
        return subprocess.run([sys.executable, str(SCRIPT), "--config", str(self.config_path),
                               "--home", str(self.home), "--json", *map(str, extra)],
                              capture_output=True, text=True, env=process_env)

    def test_fresh_home_plan_is_read_only_and_repeatable(self):
        first = self.run_plan()
        second = self.run_plan()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        plan = json.loads(first.stdout)
        self.assertEqual(plan["conflicts"], [])
        self.assertEqual(plan["runtime"], str(self.home / "runtime"))
        self.assertEqual({r["target"] for r in plan["rules"]},
                         {str(self.home / ".claude/CLAUDE.md"), str(self.home / ".codex/AGENTS.md")})
        self.assertTrue(plan["skills"])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_existing_foreign_rules_and_skills_are_unchanged(self):
        (self.home / ".claude/skills/tagesstart").mkdir(parents=True)
        (self.home / ".codex").mkdir()
        (self.home / ".agents/skills/terminvorbereitung").mkdir(parents=True)
        rule = self.home / ".claude/CLAUDE.md"
        rule.write_bytes(b"foreign rule")
        override = self.home / ".codex/AGENTS.override.md"
        override.write_bytes(b"foreign override")
        skill = self.home / ".agents/skills/terminvorbereitung/SKILL.md"
        skill.write_bytes(b"foreign skill")
        result = self.run_plan()
        self.assertEqual(result.returncode, 1)
        plan = json.loads(result.stdout)
        self.assertTrue(any("CLAUDE.md" in item for item in plan["conflicts"]))
        self.assertTrue(any("AGENTS.override.md" in item for item in plan["conflicts"]))
        self.assertTrue(any("terminvorbereitung" in item for item in plan["conflicts"]))
        self.assertEqual(rule.read_bytes(), b"foreign rule")
        self.assertEqual(override.read_bytes(), b"foreign override")
        self.assertEqual(skill.read_bytes(), b"foreign skill")

    def test_runtime_and_parent_conflicts(self):
        (self.home / "runtime").mkdir()
        result = self.run_plan()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("Runtime" in item for item in json.loads(result.stdout)["conflicts"]))
        (self.home / "runtime").rmdir()
        (self.home / ".agents").write_text("not a directory", encoding="utf-8")
        result = self.run_plan()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("Datei statt Ordner" in item for item in json.loads(result.stdout)["conflicts"]))

    def test_symlink_parent_is_conflict(self):
        real = self.home / "real"
        real.mkdir()
        (self.home / ".claude").symlink_to(real, target_is_directory=True)
        result = self.run_plan()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("Symlink" in item for item in json.loads(result.stdout)["conflicts"]))
        self.assertEqual(list(real.iterdir()), [])

    def test_custom_client_dirs_and_environment_mismatch(self):
        custom_codex = self.home / "config/codex"
        custom_claude = self.home / "config/claude"
        result = self.run_plan("--codex-home", custom_codex, "--claude-config-dir", custom_claude,
                               env={"CODEX_HOME": str(self.home / "elsewhere"),
                                    "CLAUDE_CONFIG_DIR": str(self.home / "elsewhere2")})
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual({r["target"] for r in plan["rules"]},
                         {str(custom_codex / "AGENTS.md"), str(custom_claude / "CLAUDE.md")})
        self.assertEqual(plan["clarifications"], [])
        result = self.run_plan(env={"CODEX_HOME": str(custom_codex), "CLAUDE_CONFIG_DIR": str(custom_claude)})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(json.loads(result.stdout)["clarifications"]), 2)
        self.assertTrue(all("Klärung nötig" in item for item in json.loads(result.stdout)["clarifications"]))
        self.assertEqual(list(self.home.iterdir()), [])

    def test_duplicate_skill_targets_are_conflicts_even_with_aliases(self):
        for name in (".agents", ".AGENTS"):
            with self.subTest(name=name):
                result = self.run_plan("--claude-config-dir", self.home / name)
                self.assertEqual(result.returncode, 1)
                self.assertTrue(any("Doppeltes Ziel" in item or "überschneiden sich" in item for item in json.loads(result.stdout)["conflicts"]))
        self.assertEqual(list(self.home.iterdir()), [])

    def test_client_dir_must_not_overlap_private_or_package_areas(self):
        cases = (("--codex-home", self.home / "profile", "profile"),
                 ("--codex-home", self.home / "runtime", "runtime"),
                 ("--codex-home", self.home / "SOURCE", "source"),
                 ("--claude-config-dir", self.home / "output/child", "output"),
                 ("--claude-config-dir", self.home, "Benutzerordner"),
                 ("--codex-home", Path("/"), "Systemwurzel"))
        for option, path, label in cases:
            with self.subTest(option=option, path=path):
                result = self.run_plan(option, path)
                self.assertEqual(result.returncode, 1)
                self.assertTrue(any(label in item for item in json.loads(result.stdout)["conflicts"]))
        self.config["paths"]["output"] = "~/Café"
        result = self.run_plan("--claude-config-dir", self.home / "Cafe\u0301")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("paths.output" in item for item in json.loads(result.stdout)["conflicts"]))

    def test_codex_skill_base_must_not_overlap_any_configured_area(self):
        self.config["clients"] = ["codex"]
        original_paths = dict(self.config["paths"])
        for area in ("source", "runtime", "profile", "output"):
            for alias in ("~/.agents", "~/.AGENTS"):
                with self.subTest(area=area, alias=alias):
                    self.config["paths"] = dict(original_paths)
                    self.config["paths"][area] = alias
                    result = self.run_plan()
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertTrue(any(f"Codex-Skillbasis überschneidet sich mit paths.{area}" in item
                                        for item in json.loads(result.stdout)["conflicts"]))
        self.assertEqual(list(self.home.iterdir()), [])

    def test_explicit_client_path_symlink_parent_rejected(self):
        real = self.home / "real"
        real.mkdir()
        (self.home / "alias").symlink_to(real, target_is_directory=True)
        result = self.run_plan("--codex-home", self.home / "alias/config")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("Symlink" in item for item in json.loads(result.stdout)["conflicts"]))
        self.assertEqual(list(real.iterdir()), [])

    def test_existing_output_and_metadata_are_not_read_or_changed(self):
        output = self.home / "output"
        output.mkdir()
        marker = output / "private.txt"
        marker.write_bytes(b"private marker")
        (self.home / ".claude").mkdir()
        (self.home / ".codex").mkdir()
        for path in (self.home / ".claude/settings.json", self.home / ".claude/.mcp.json",
                     self.home / ".codex/config.toml"):
            path.write_bytes(b"invalid and private content")
        result = self.run_plan()
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertIn("vorhanden", " ".join(plan["observations"]).lower())
        self.assertNotIn("invalid and private content", result.stdout)
        self.assertEqual(marker.read_bytes(), b"private marker")

    def test_invalid_config_rejected_without_target_reads(self):
        self.config["confirmed"] = False
        result = self.run_plan()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
