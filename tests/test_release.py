"""Reject release labels that lack matching metadata and dated notes."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release_check', Path(__file__).resolve().parents[1] / 'scripts/check_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def test_proposed_tag_requires_matching_version_and_dated_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'SKILL.md').write_text('---\nmetadata:\n  version: "4.2.1"\n---\n')
            (root / 'CHANGELOG.md').write_text('# Changelog\n\n## Unreleased\n')
            self.assertEqual(release.check(root), '4.2.1')
            with self.assertRaisesRegex(ValueError, 'does not match'):
                release.check(root, 'v4.2.2')
            with self.assertRaisesRegex(ValueError, 'Missing dated'):
                release.check(root, 'v4.2.1')
            with (root / 'CHANGELOG.md').open('a') as stream:
                stream.write('\n## 4.2.1 - 2026-09-07\n\n- Verified change.\n')
            self.assertEqual(release.check(root, 'v4.2.1'), '4.2.1')
