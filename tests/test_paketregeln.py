import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


PACKAGE = Path(__file__).resolve().parents[1]


class PackagePolicyTests(unittest.TestCase):
    def load(self, name):
        with patch.object(sys, "path", [str(PACKAGE / "scripts"), *sys.path]):
            spec = importlib.util.spec_from_file_location(name, PACKAGE / "scripts" / f"{name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    def test_private_paths_and_invalid_names_rejected_by_one_policy(self):
        policy = self.load("paketregeln")
        for raw in ("allgemein/secrets/token.txt", "allgemein/credentials/token.txt",
                    "allgemein/journals/action.json", "allgemein/profil.md", ".env",
                    "allgemein/foo/../bar.md", "/allgemein/x.md", "allgemein/x\x00.md"):
            with self.subTest(raw=raw):
                self.assertFalse(policy.allowed_file(raw))
        for raw in ("allgemein/secrets", "allgemein/credentials", "allgemein/journals"):
            self.assertFalse(policy.allowed_directory(raw))

    def test_approved_templates_and_regular_package_are_accepted(self):
        policy = self.load("paketregeln")
        builder = self.load("paket_bauen")
        self.assertTrue(all(policy.allowed_file(raw) for raw in policy.TEMPLATES))
        self.assertTrue(all(policy.allowed_directory(raw) for raw in policy.TEMPLATE_DIRS))
        snapshot = builder.source_snapshot()
        contents = builder.package_contents(snapshot)
        for relative in contents:
            if relative.as_posix() != "paket.json":
                self.assertTrue(policy.allowed_file(relative.as_posix()), relative)
        self.assertIn(Path("scripts/paketregeln.py"), contents)

    def test_env_example_exception_is_only_for_a_file(self):
        policy = self.load("paketregeln")
        for raw in ("allgemein/.env.example/token.txt",
                    "allgemein/konfiguration/.ENV.EXAMPLE/nested/file.md"):
            with self.subTest(raw=raw):
                self.assertFalse(policy.allowed_file(raw))
        self.assertTrue(policy.allowed_file("allgemein/.env.example"))
        self.assertTrue(policy.allowed_file("allgemein/konfiguration/.env.example"))


if __name__ == "__main__":
    unittest.main()
