import hashlib
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
RENDERER = PACKAGE / "de/werkzeuge/unterlagen/render.py"
CHECKER = PACKAGE / "de/werkzeuge/praesentationen/check_html.py"


class RendererTransferTests(unittest.TestCase):
    """German tool tree. EnglishRendererTransferTests repeats every case for the English tree."""
    language = "de"
    renderer = RENDERER
    checker = CHECKER
    runtime_renderer = "allgemein/werkzeuge/unterlagen/render.py"
    profile = "profiles/hausformat.css"
    duplicate_message = "Doppelter JSON-Schlüssel"
    external_message = "Externe Ressourcen oder Netzwerkaufrufe vorhanden"

    def setUp(self):
        if not self.renderer.is_file() or not self.checker.is_file():
            self.skipTest(f"Tool tree for {self.language} not present")
        self.temp = tempfile.TemporaryDirectory(prefix=".aios-test-", dir=PACKAGE.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.content = self.root / "synthetic.json"
        self.palette = self.root / "palette.md"
        self.output = self.root / "output"
        self.data = {
            "schema_version": 1,
            "meta": {"title": "Synthetische Schulung", "customer": "Testfirma", "subtitle": "Nur Testdaten",
                     "date": "2026-10-20", "version": "1", "author": "Test"},
            "case": {"title": "Testfall", "description": "Ein erfundener Ablauf"},
            "chapters": [{"id": "kapitel", "title": "Grundlagen", "summary": "Kurz und klar",
                          "fields": ["Eigener Schritt"],
                          "slides": [{"id": "folie", "title": "Prüfen", "text": "Synthetischer Inhalt",
                                      "points": ["Erster Punkt"], "mins": 5, "notes": "Nur Trainer"}]}],
            "examples": [], "sources": [],
        }
        self.content.write_text(json.dumps(self.data), encoding="utf-8")
        self.palette.write_text('```json\n' + json.dumps({
            "schema_version": 1, "palettes": {"test": {"primary": "#123456", "accent": "#ABCDEF",
                                                     "ink": "#111111", "notice": "Synthetische Palette"}}
        }) + '\n```\n', encoding="utf-8")

    def run_cli(self, *extra, script=None, cwd=None):
        script = script or self.renderer
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        return subprocess.run([sys.executable, str(script), "--input", str(self.content),
                               "--output", str(self.output), "--palette-file", str(self.palette),
                               "--palette", "test", *map(str, extra)], capture_output=True,
                              text=True, cwd=cwd, env=env, timeout=10)

    def load_renderer(self):
        spec = importlib.util.spec_from_file_location("transferred_renderer_" + self.language, self.renderer)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_cli_builds_selected_outputs_and_hashes(self):
        result = self.run_cli("--artifacts", "handout")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.output / "02_handout.html").is_file())
        self.assertFalse((self.output / "01_praesentation.html").exists())
        self.assertNotIn("Nur Trainer", (self.output / "02_handout.html").read_text())
        manifest = json.loads((self.output / "build.json").read_text())
        for name, digest in manifest["files"].items():
            self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(), digest)
        self.assertEqual(manifest["palette_name"], "test")

    def test_palette_is_required_and_duplicate_json_keys_fail(self):
        missing = subprocess.run([sys.executable, str(self.renderer), "--input", str(self.content),
                                  "--output", str(self.output)], capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertFalse(self.output.exists())
        self.content.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        duplicate = self.run_cli()
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn(self.duplicate_message, duplicate.stderr)
        self.assertFalse(self.output.exists())

    def test_schema_failure_is_read_only(self):
        self.data["chapters"][0]["slides"][0]["prompt_ids"] = ["missing"]
        self.content.write_text(json.dumps(self.data), encoding="utf-8")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_duplicate_palette_keys_are_rejected_before_writing(self):
        self.palette.write_text(self.palette.read_text().replace(
            '"primary": "#123456"', '"primary": "#123456", "primary": "#654321"'),
            encoding="utf-8")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(self.duplicate_message, result.stderr)
        self.assertFalse(self.output.exists())

    def test_empty_target_created_immediately_before_publish_is_preserved(self):
        renderer = self.load_renderer()
        import safe_files as sichere_dateien
        rename = sichere_dateien.exclusive_rename_at
        identities = []
        def create_empty_target(parent_fd, source_name, destination_name):
            os.mkdir(destination_name, dir_fd=parent_fd)
            info = os.stat(destination_name, dir_fd=parent_fd)
            identities.append((info.st_dev, info.st_ino))
            return rename(parent_fd, source_name, destination_name)
        args = type("Args", (), {"input": self.content, "output": self.output,
                                  "palette_file": self.palette, "palette": "test",
                                  "profile": renderer.ASSETS / self.profile,
                                  "artifacts": ["presentation"]})()
        with patch.object(sichere_dateien, "exclusive_rename_at", side_effect=create_empty_target):
            with self.assertRaises(OSError):
                renderer.build(args)
        info = self.output.stat()
        self.assertEqual(identities, [(info.st_dev, info.st_ino)])
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertEqual(list(self.root.glob(".aios-paket-*")), [])

    def test_existing_target_and_race_target_remain_unchanged(self):
        self.output.mkdir()
        marker = self.output / "marker.txt"
        marker.write_bytes(b"foreign")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_bytes(), b"foreign")
        marker.unlink()
        self.output.rmdir()
        renderer = self.load_renderer()
        original_build = renderer.build_directory
        def create_target_then_publish(path, contents):
            Path(path).mkdir()
            (Path(path) / "marker.txt").write_bytes(b"foreign race")
            return original_build(path, contents)
        args = type("Args", (), {"input": self.content, "output": self.output, "palette_file": self.palette,
                                  "palette": "test", "profile": renderer.ASSETS / self.profile,
                                  "artifacts": ["presentation"]})()
        with patch.object(renderer, "build_directory", side_effect=create_target_then_publish):
            with self.assertRaises(OSError):
                renderer.build(args)
        self.assertEqual((self.output / "marker.txt").read_bytes(), b"foreign race")

    def test_checker_blocks_resource_attributes(self):
        spec = importlib.util.spec_from_file_location("transferred_checker_" + self.language, self.checker)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for markup in ('<img srcset="https://example.invalid/a.png 1x">',
                       '<form action="https://example.invalid/post"></form>',
                       '<button formaction="https://example.invalid/send">Senden</button>',
                       '<video poster="https://example.invalid/poster.png"></video>',
                       '<img srcset="data:image/png;base64,AAAA 1x, https://example.invalid/a.png 2x">',
                       '<a ping="https://example.invalid/track" href="#local">Text</a>',
                       '<iframe srcdoc="&lt;img src=https://example.invalid/a.png&gt;"></iframe>',
                       '<div style="background:url(https://example.invalid/a.png)"></div>',
                       '<meta http-equiv="refresh" content="0;url=https://example.invalid/">'):
            with self.subTest(markup=markup):
                result = module.inspect_html('<section id="s1">' + markup + '</section>')
                self.assertIn(self.external_message, result["errors"])

    def test_renderer_runs_from_bundled_runtime_outside_source_cwd(self):
        with patch.object(sys, "path", [str(PACKAGE / "scripts"), *sys.path]):
            import build_package as paket_bauen
            contents = paket_bauen.package_contents(paket_bauen.source_snapshot(self.language), self.language)
        runtime = self.root / "runtime"
        import safe_files as sichere_dateien
        sichere_dateien.build_directory(runtime, contents)
        isolated = self.root / "isolated"
        isolated.mkdir()
        script = runtime / self.runtime_renderer
        result = self.run_cli("--artifacts", "examples", script=script, cwd=isolated)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.output / "03_beispiele.html").exists())


class EnglishRendererTransferTests(RendererTransferTests):
    language = "en"
    renderer = PACKAGE / "en/tools/materials/render.py"
    checker = PACKAGE / "en/tools/presentations/check_html.py"
    runtime_renderer = "general/tools/materials/render.py"
    profile = "profiles/house-style.css"
    duplicate_message = "Duplicate JSON key"
    external_message = "External resources or network calls present"


if __name__ == "__main__":
    unittest.main()
