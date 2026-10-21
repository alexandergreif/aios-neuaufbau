import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pruefe_konfiguration.py"


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.config_path = self.base / "config.json"
        self.config = {
            "schema_version": 1,
            "confirmed": True,
            "clients": ["claude-code", "codex"],
            "paths": {
                "source": "~/source",
                "runtime": "~/aios-runtime",
                "profile": "~/aios-profile",
                "output": "~/aios-output",
                "coding_roots": ["~/coding"],
                "customer_roots": ["~/customers"],
            },
        }

    def run_check(self, config=None, raw=None, home=None):
        self.config_path.write_text(raw if raw is not None else json.dumps(config or self.config), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(self.config_path), "--home", str(home or self.home)],
            capture_output=True, text=True, check=False,
        )

    def test_valid_configuration_does_not_create_target_directories(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_unconfirmed_template_is_rejected(self):
        self.config["confirmed"] = False
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_missing_required_choices_are_rejected(self):
        for field, value in (("clients", []), ("source", None), ("coding_roots", None), ("customer_roots", None)):
            with self.subTest(field=field):
                config = copy.deepcopy(self.config)
                if field == "clients":
                    config[field] = value
                else:
                    config["paths"][field] = value
                self.assertNotEqual(self.run_check(config).returncode, 0)

    def test_confirmed_empty_project_root_lists_are_valid(self):
        self.config["paths"]["coding_roots"] = []
        self.config["paths"]["customer_roots"] = []
        self.assertEqual(self.run_check().returncode, 0)

    def test_source_can_be_inside_coding_root_but_not_equal_to_it(self):
        self.config["paths"]["source"] = "~/coding/AIOS-Neuaufbau"
        self.assertEqual(self.run_check().returncode, 0)
        self.config["paths"]["source"] = "~/coding"
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_invalid_path_forms_are_rejected_without_echoing_values(self):
        for value in ("relative/path", "~other/private", "~/../private", "~//outside", "$PRIVATE/path", "/", "//"):
            with self.subTest(value=value):
                self.config["paths"]["runtime"] = value
                result = self.run_check()
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(value, result.stderr)

    def test_area_and_project_root_overlap_are_rejected(self):
        for field, value in (("profile", "~/aios-runtime/private"),
                             ("source", "~/customers/source"),
                             ("coding_roots", ["~/aios-output/projects"]),
                             ("customer_roots", ["~/coding/team"])):
            with self.subTest(field=field):
                config = copy.deepcopy(self.config)
                config["paths"][field] = value
                self.assertNotEqual(self.run_check(config).returncode, 0)

    def test_existing_symlink_alias_is_rejected(self):
        (self.home / "real").mkdir()
        (self.home / "alias").symlink_to(self.home / "real")
        self.config["paths"]["runtime"] = "~/real"
        self.config["paths"]["profile"] = "~/alias"
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_case_difference_is_rejected_for_existing_directory(self):
        (self.home / "Runtime").mkdir()
        self.config["paths"]["runtime"] = "~/Runtime"
        self.config["paths"]["profile"] = "~/runtime"
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_case_difference_is_rejected_for_missing_nested_directory(self):
        self.config["paths"]["runtime"] = "~/NewFolder"
        self.config["paths"]["profile"] = "~/newfolder/private"
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_unicode_normal_forms_are_rejected_as_same_path(self):
        self.config["paths"]["runtime"] = "~/Café"
        self.config["paths"]["profile"] = "~/Cafe\u0301/private"
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_home_alias_by_case_or_unicode_is_rejected(self):
        for value in (str(self.base / "HOME"), str(self.base / "homé")):
            with self.subTest(value=value):
                if "homé" in value:
                    home = self.base / "home\u0301"
                    home.mkdir()
                else:
                    home = self.home
                config = copy.deepcopy(self.config)
                for field in ("source", "profile", "output"):
                    config["paths"][field] = str(self.base / ("separate-" + field))
                config["paths"]["coding_roots"] = []
                config["paths"]["customer_roots"] = []
                config["paths"]["runtime"] = value
                result = self.run_check(config, home=home)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Benutzerordner", result.stderr)

    def test_double_slash_home_is_rejected(self):
        self.assertNotEqual(self.run_check(home=Path("//")).returncode, 0)

    def test_source_inside_coding_root_uses_normalized_comparison(self):
        self.config["paths"]["coding_roots"] = ["~/Coding-Café"]
        self.config["paths"]["source"] = "~/coding-cafe\u0301/AIOS"
        self.assertEqual(self.run_check().returncode, 0)

    def test_symlink_loop_is_rejected(self):
        (self.home / "loop").symlink_to("loop")
        self.config["paths"]["runtime"] = "~/loop"
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_symlink_loop_as_home_is_rejected(self):
        loop = self.base / "loop"
        loop.symlink_to("loop")
        self.assertNotEqual(self.run_check(home=loop).returncode, 0)

    def test_existing_file_as_target_or_parent_is_rejected(self):
        (self.home / "file").write_text("synthetic", encoding="utf-8")
        for value in ("~/file", "~/file/child"):
            with self.subTest(value=value):
                self.config["paths"]["runtime"] = value
                self.assertNotEqual(self.run_check().returncode, 0)

    def test_unknown_and_duplicate_keys_are_rejected(self):
        config = copy.deepcopy(self.config)
        config["paths"]["profle"] = "~/typo"
        self.assertNotEqual(self.run_check(config).returncode, 0)
        raw = json.dumps(self.config).replace('"confirmed": true', '"confirmed": true, "confirmed": true')
        self.assertNotEqual(self.run_check(raw=raw).returncode, 0)

    def test_invalid_json_and_unknown_client_are_rejected_without_dump(self):
        result = self.run_check(raw='{"secret": "do-not-print",')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("do-not-print", result.stderr)
        self.config["clients"] = ["unknown"]
        self.assertNotEqual(self.run_check().returncode, 0)


if __name__ == "__main__":
    unittest.main()
