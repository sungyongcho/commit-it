"""Check shared installation and updates without writing to actual agent directories."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'home with spaces'
        self.source = Path(self.temp.name) / 'source'
        for name, content in {'SKILL.md': '---\nname: commit-it\ndescription: Fixture\n---\nHello\n',
                'agents/openai.yaml': 'interface: {}\n', 'scripts/protect-branch.sh': '#!/bin/sh\n',
                'references/test.md': 'Reference\n'}.items():
            p = self.source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        self.destination = self.home / 'Documents/skills/commit-it'

    def run_install(self, **kwargs):
        return installer.install(self.source, self.destination, ['codex', 'claude', 'gemini'], home=self.home, **kwargs)

    def test_all_agents_share_one_complete_source(self):
        result = self.run_install()
        self.assertEqual(len(result['targets']), 2)
        self.assertTrue((self.destination / 'references/test.md').is_file())
        for path in result['targets']:
            self.assertEqual(Path(path).resolve(), self.destination)
        self.assertEqual(self.run_install()['files'], result['files'])

    def test_dry_run_does_not_create_files(self):
        self.run_install(dry_run=True)
        self.assertFalse(self.home.exists())

    def test_update_is_explicit_and_refuses_local_changes(self):
        self.run_install()
        (self.source / 'references/test.md').write_text('New reference\n')
        with self.assertRaisesRegex(installer.InstallError, '--update'):
            self.run_install()
        self.run_install(update=True)
        (self.destination / 'references/test.md').write_text('My local work\n')
        with self.assertRaisesRegex(installer.InstallError, 'Local changes'):
            self.run_install(update=True)
        self.assertEqual((self.destination / 'references/test.md').read_text(), 'My local work\n')

    def test_existing_legacy_copy_is_preserved(self):
        legacy = self.home / '.codex/skills/commit-it'
        legacy.mkdir(parents=True)
        (legacy / 'mine').write_text('Keep\n')
        with self.assertRaisesRegex(installer.InstallError, 'legacy'):
            self.run_install()
        self.assertTrue((legacy / 'mine').is_file())

    def test_failure_restores_previous_source(self):
        self.run_install()
        old = (self.destination / 'SKILL.md').read_bytes()
        (self.source / 'SKILL.md').write_text('---\nname: commit-it\n---\nNew\n')
        original = installer.os.rename
        def fail(source, target):
            if Path(source).name == 'commit-it' and '.commit-it-stage-' in str(source):
                raise OSError('Fixture failure')
            return original(source, target)
        with patch.object(installer.os, 'rename', fail), self.assertRaises(OSError):
            self.run_install(update=True)
        self.assertEqual((self.destination / 'SKILL.md').read_bytes(), old)

    def test_local_checkout_can_be_linked_without_copying_itself(self):
        self.destination = self.source
        self.run_install()
        self.assertFalse((self.source / installer.MARKER).exists())
        self.assertTrue((self.home / '.claude/skills/commit-it').is_symlink())


if __name__ == '__main__':
    unittest.main()
