import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'pruefe_register.py'
HEADER = '| Kürzel | Kunde oder Projekt | Lokaler Ordner | Repository | Jira-Präfix | Status |\n| --- | --- | --- | --- | --- | --- |\n'


class RegisterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.config = {'schema_version': 1, 'confirmed': True, 'clients': ['codex'], 'paths': {
            'source': '~/code/AIOS', 'runtime': '~/runtime', 'profile': '~/profile',
            'output': '~/output', 'coding_roots': ['~/code'], 'customer_roots': ['~/customers']}}
        self.config_path = self.home / 'paths.json'
        self.config_path.write_text(json.dumps(self.config))
        self.register = self.home / 'projekte.md'

    def run_check(self, rows='', project=None, header=HEADER):
        self.register.write_text(header + rows)
        args = [sys.executable, str(SCRIPT), '--register', str(self.register),
                '--config', str(self.config_path), '--home', str(self.home)]
        if project is not None:
            args += ['--project', project]
        return subprocess.run(args, capture_output=True, text=True)

    def row(self, key='DEMO', path=None, status='aktiv', repo='https://example.org/repo'):
        return f'| {key} | Synthetisches Projekt | {path or self.home / "customers/demo"} | {repo} | TEST | {status} |\n'

    def test_empty_and_unassigned_are_valid_but_not_routable(self):
        self.assertEqual(self.run_check().returncode, 0)
        pending = '| DEMO | Synthetisch | | | | zuordnen |\n'
        self.assertEqual(self.run_check(pending).returncode, 0)
        self.assertNotEqual(self.run_check(pending, 'DEMO').returncode, 0)

    def test_active_project_resolves_without_creating_or_reading_project(self):
        result = self.run_check(self.row(), 'demo')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), str((self.home / 'customers/demo').resolve()))
        self.assertFalse((self.home / 'customers').exists())

    def test_unknown_or_paused_project_needs_clarification(self):
        self.assertNotEqual(self.run_check(self.row(), 'OTHER').returncode, 0)
        self.assertNotEqual(self.run_check(self.row(status='pausiert'), 'DEMO').returncode, 0)

    def test_duplicate_keys_and_mac_path_aliases_rejected(self):
        for rows in [self.row() + self.row('demo', self.home / 'customers/other'),
                     self.row() + self.row('OTHER', self.home / 'customers/DEMO')]:
            with self.subTest(rows=rows):
                self.assertNotEqual(self.run_check(rows).returncode, 0)

    def test_outside_roots_source_and_traversal_rejected(self):
        for path in [self.home / 'outside/demo', self.home / 'code/AIOS/sub',
                     self.home / 'customers/../output/demo', self.home / 'customers']:
            with self.subTest(path=path):
                self.assertNotEqual(self.run_check(self.row(path=path)).returncode, 0)

    def test_repository_credentials_are_rejected_without_echo(self):
        for repo in ['https://user:TEST_SECRET@example.org/x',
                     'https://example.org/x?token=TEST_SECRET']:
            result = self.run_check(self.row(repo=repo))
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('TEST_SECRET', result.stdout + result.stderr)

    def test_bad_table_or_status_rejected(self):
        for args in [dict(header='| bad |\n'), dict(rows=self.row(status='whatever')),
                     dict(rows='| DEMO | too few |\n'), dict(header=HEADER + HEADER)]:
            with self.subTest(args=args):
                self.assertNotEqual(self.run_check(**args).returncode, 0)

    def test_symlink_escape_is_rejected(self):
        (self.home / 'customers').mkdir()
        (self.home / 'outside').mkdir()
        (self.home / 'customers/demo').symlink_to(self.home / 'outside', target_is_directory=True)
        self.assertNotEqual(self.run_check(self.row()).returncode, 0)


if __name__ == '__main__':
    unittest.main()
