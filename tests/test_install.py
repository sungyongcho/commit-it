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
        self.home = Path(self.temp.name).resolve() / 'home with spaces'
        self.source = Path(self.temp.name).resolve() / 'source'
        contents = {name: 'Fixture content\n' for name in installer.PACKAGE_FILES}
        contents.update({'SKILL.md': '---\nname: commit-it\ndescription: Fixture\nmetadata:\n  version: "2.9.0"\n---\nHello\n',
            'agents/openai.yaml': 'interface: {}\n', 'scripts/protect-branch.sh': '#!/bin/sh\n'})
        for name, content in contents.items():
            p = self.source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        self.destination = self.home / 'Documents/skills/commit-it'

    def run_install(self, **kwargs):
        return installer.install(self.source, self.destination, ['codex', 'claude', 'gemini'], home=self.home, **kwargs)

    def test_all_agents_share_one_complete_source(self):
        result = self.run_install()
        self.assertEqual(len(result['targets']), 2)
        self.assertTrue((self.destination / 'references/pr-review.md').is_file())
        for path in result['targets']:
            self.assertEqual(Path(path).resolve(), self.destination)
        self.assertEqual(self.run_install()['files'], result['files'])

    def test_dry_run_does_not_create_files(self):
        self.run_install(dry_run=True)
        self.assertFalse(self.home.exists())

    def test_update_is_explicit_and_refuses_local_changes(self):
        self.run_install()
        (self.source / 'references/pr-review.md').write_text('New reference\n')
        with self.assertRaisesRegex(installer.InstallError, '--update'):
            self.run_install()
        self.run_install(update=True)
        (self.destination / 'references/pr-review.md').write_text('My local work\n')
        with self.assertRaisesRegex(installer.InstallError, 'Local changes'):
            self.run_install(update=True)
        self.assertEqual((self.destination / 'references/pr-review.md').read_text(), 'My local work\n')

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


    def test_package_inventory_is_explicit_and_excludes_local_maintenance_files(self):
        (self.source / 'private-notes.md').write_text('Keep out of installed packages')
        result = self.run_install()
        self.assertEqual(set(result['files']), set(installer.PACKAGE_FILES))
        self.assertEqual(len(result['files']), 11)
        self.assertFalse((self.destination / 'private-notes.md').exists())

    def test_successful_update_retains_the_complete_previous_copy(self):
        self.run_install()
        original = installer._managed(self.destination)
        (self.source / 'README.md').write_text('Reviewed new instructions\n')
        result = self.run_install(update=True)
        backup = Path(result['backup'])
        self.assertTrue(backup.is_dir())
        self.assertNotIn('.commit-it-stage-', str(backup))
        self.assertEqual(installer._managed(backup), original)
        self.assertEqual((self.destination / 'README.md').read_text(), 'Reviewed new instructions\n')

    def test_git_authoring_source_is_linked_in_place_but_never_copy_replaced(self):
        self.run_install()
        (self.destination / '.git').mkdir()
        (self.destination / '.git/HEAD').write_text('ref: refs/heads/main\n')
        (self.destination / 'AGENTS.md').write_text('Preserve local rules\n')
        before = (self.destination / 'SKILL.md').read_bytes()
        with self.assertRaisesRegex(installer.InstallError, 'editable Git source'):
            self.run_install(update=True)
        result = installer.install(self.destination, self.destination, ['codex', 'claude'], home=self.home)
        self.assertEqual(result['mode'], 'source-links')
        self.assertIsNone(result['backup'])
        self.assertEqual((self.destination / 'SKILL.md').read_bytes(), before)
        self.assertEqual((self.destination / '.git/HEAD').read_text(), 'ref: refs/heads/main\n')
        self.assertEqual((self.destination / 'AGENTS.md').read_text(), 'Preserve local rules\n')

    def test_managed_updates_reject_extra_cache_directories_and_mode_changes(self):
        self.run_install()
        extra = self.destination / '__pycache__'
        extra.mkdir()
        with self.assertRaisesRegex(installer.InstallError, 'Local changes'):
            self.run_install(update=True)
        self.assertTrue(extra.is_dir())
        extra.rmdir()
        script = self.destination / 'scripts/protect-branch.sh'
        script.chmod(0o700)
        with self.assertRaisesRegex(installer.InstallError, 'Local changes'):
            self.run_install(update=True)
        self.assertEqual(script.stat().st_mode & 0o777, 0o700)

    def test_source_change_during_staging_preserves_the_installed_copy(self):
        self.run_install()
        (self.source / 'README.md').write_text('Reviewed update')
        stage = installer._stage
        def changed(*args):
            """Simulate another owner changing installed content after initial inspection."""
            result = stage(*args)
            (self.destination / 'README.md').write_text('Concurrent local change')
            return result
        with patch.object(installer, '_stage', changed), self.assertRaises(installer.InstallError):
            self.run_install(update=True)
        self.assertEqual((self.destination / 'README.md').read_text(), 'Concurrent local change')

    def test_redirected_discovery_parent_is_rejected_before_source_or_link_creation(self):
        outside = self.home / 'unrelated'
        outside.mkdir(parents=True)
        (outside / 'sentinel').write_text('Preserve')
        (self.home / '.agents').mkdir()
        (self.home / '.agents/skills').symlink_to(outside, target_is_directory=True)
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run), self.assertRaisesRegex(installer.InstallError, 'Redirected parent'):
                self.run_install(dry_run=dry_run)
        self.assertFalse(self.destination.exists())
        self.assertFalse((outside / 'commit-it').exists())
        self.assertEqual((outside / 'sentinel').read_text(), 'Preserve')

    def test_redirected_destination_parent_is_rejected_without_changing_its_target(self):
        outside = self.home / 'unrelated'
        outside.mkdir(parents=True)
        (self.home / 'Documents').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(installer.InstallError, 'Redirected parent'):
            self.run_install()
        self.assertEqual(list(outside.iterdir()), [])
        self.assertTrue((self.home / 'Documents').is_symlink())
        self.assertFalse((self.home / '.agents').exists())

    def test_late_redirected_discovery_link_is_preserved(self):
        discovery = installer._discovery
        calls = []
        foreign = self.home / 'foreign'
        foreign.mkdir(parents=True)
        def changed(*args):
            """Introduce an unexpected link after the first read-only preflight."""
            calls.append(True)
            if len(calls) == 2:
                target = self.home / '.claude/skills/commit-it'
                target.parent.mkdir(parents=True)
                target.symlink_to(foreign, target_is_directory=True)
            return discovery(*args)
        with patch.object(installer, '_discovery', changed), self.assertRaises(installer.InstallError):
            self.run_install()
        self.assertFalse(self.destination.exists())
        self.assertEqual((self.home / '.claude/skills/commit-it').resolve(), foreign)

    def test_link_failure_restores_old_content_and_retains_backup(self):
        installer.install(self.source, self.destination, ['codex'], home=self.home)
        old = (self.destination / 'README.md').read_bytes()
        (self.source / 'README.md').write_text('Reviewed update')
        symlink = Path.symlink_to
        def fail(path, *args, **kwargs):
            """Fail only the new Claude link after the new package is published."""
            if '.claude' in path.parts:
                raise OSError('Fixture link failure')
            return symlink(path, *args, **kwargs)
        with patch.object(Path, 'symlink_to', fail), self.assertRaises(OSError):
            self.run_install(update=True)
        self.assertEqual((self.destination / 'README.md').read_bytes(), old)
        backups = list((self.destination.parent / '.commit-it-backups').glob('*/source'))
        self.assertTrue(any((backup / 'README.md').read_bytes() == old for backup in backups))
        self.assertEqual((self.home / '.agents/skills/commit-it').resolve(), self.destination)

    def test_revision_is_not_claimed_for_dirty_package_bytes(self):
        data = installer.package(self.source)
        def git(args, **kwargs):
            """Provide a real-shaped Git response without making fixture commits."""
            if args[-1] == '--show-toplevel':
                output = str(self.source).encode() + b'\n'
            elif args[-1] == 'HEAD':
                output = b'a' * 40 + b'\n'
            else:
                name = args[-1].split(':', 1)[1]
                output = b'Different committed README' if name == 'README.md' else data[name]
            return installer.subprocess.CompletedProcess(args, 0, output, b'')
        with patch.object(installer.subprocess, 'run', git):
            self.assertIsNone(installer._revision(self.source, data))


if __name__ == '__main__':
    unittest.main()
