"""Ensure the retired installer cannot recreate product links or copies."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/install.py'


class RetiredInstallerTests(unittest.TestCase):
    def test_legacy_invocations_refuse_without_touching_home(self):
        """Old scripts fail explicitly while preserving native product and user state."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / 'native-skill'; existing.mkdir()
            (existing / 'SKILL.md').write_text('Keep native state')
            for args in ([], ['--agent', 'both'], ['--agent', 'all', '--update'],
                         ['--source', str(existing), '--destination', str(root / 'shared')]):
                result = subprocess.run([sys.executable, str(SCRIPT), *args],
                    env={**os.environ, 'HOME': str(root)}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn('no installation was performed', result.stderr)
                self.assertEqual((existing / 'SKILL.md').read_text(), 'Keep native state')
                self.assertEqual([p.name for p in root.iterdir()], ['native-skill'])


if __name__ == '__main__':
    unittest.main()
