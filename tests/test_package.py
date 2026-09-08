"""Validate public package boundaries and protection-helper payloads without GitHub writes."""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_skill_has_metadata_and_local_references(self):
        text = (ROOT / 'SKILL.md').read_text()
        self.assertTrue(text.startswith('---\nname: commit-it\n'))
        self.assertIn('description:', text.split('---', 2)[1])
        self.assertRegex(text, r'version: "\d+\.\d+\.\d+"')
        for file in [ROOT / 'SKILL.md', ROOT / 'README.md', *ROOT.joinpath('docs').glob('*.md'), *ROOT.joinpath('references').glob('*.md')]:
            for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                if '://' not in link and not link.startswith('#'):
                    self.assertTrue((file.parent / link.split('#')[0]).exists(), link)

    def test_controller_record_schemas_are_not_duplicated_in_the_skill(self):
        """Project controllers remain the only source of operational record schemas."""
        for file in [ROOT / 'SKILL.md', *ROOT.joinpath('references').glob('*.md')]:
            text = file.read_text()
            self.assertNotIn('<!-- ops:', text)
            self.assertNotIn('<!-- commit-it:work-state:', text)
            self.assertNotIn('opsctl ', text)

    def test_package_excludes_private_routing_and_product_install_targets(self):
        """Public guidance must remain portable across hosts, accounts and native installers."""
        for file in [ROOT / 'SKILL.md', *ROOT.joinpath('references').glob('*.md'), ROOT / 'agents/openai.yaml']:
            text = file.read_text()
            for private in ('/home/', '/Users/', 'Documents/', 'ops:global-policy', '-----BEGIN PRIVATE KEY-----', '.agents/skills', '.claude/skills'):
                self.assertNotIn(private, text, str(file))
            self.assertNotRegex(text, r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', str(file))

    def test_review_modes_preserve_the_exact_eligible_headings(self):
        """Generic Git guidance still distinguishes separate review, self-review and resolution."""
        expected = {'Self-review: LGTM', 'Review: LGTM', 'Conflict resolution: LGTM'}
        for relative in ('SKILL.md', 'references/pr-review.md', 'references/worker-coordination.md'):
            text = (ROOT / relative).read_text()
            self.assertIn('conflict-resolution.md)', text, relative)
            self.assertEqual(set(re.findall(r'`((?:Self-review|Review|Conflict resolution): LGTM)`', text)), expected)

    def run_helper(self, arguments):
        """Replace gh with a fixture recorder so protection is never changed by tests."""
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        executable = root / 'gh'
        executable.write_text('#!/usr/bin/env python3\nimport json,os,sys\nfrom pathlib import Path\nPath(os.environ["CAPTURE"]).write_text(json.dumps({"args":sys.argv[1:],"body":json.load(sys.stdin)}))\n')
        executable.chmod(0o755)
        output = root / 'payload.json'
        result = subprocess.run(['sh', str(ROOT / 'scripts/protect-branch.sh'), *arguments],
                                env={**os.environ, 'PATH': str(root) + os.pathsep + os.environ['PATH'], 'CAPTURE': str(output)},
                                capture_output=True, text=True)
        return result, json.loads(output.read_text()) if output.exists() else None

    def test_default_profile_works_with_only_two_arguments(self):
        result, request = self.run_helper(['owner/repo', 'main'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(request['body']['enforce_admins'])
        self.assertEqual(request['body']['required_status_checks']['contexts'], [])

    def test_contexts_are_json_encoded_and_branch_is_url_encoded(self):
        contexts = ['test "quoted"', 'line\nbreak']
        result, request = self.run_helper(['owner/repo', 'release/example', 'fast', *contexts])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('repos/owner/repo/branches/release%2Fexample/protection', request['args'])
        self.assertEqual(request['body']['required_status_checks']['contexts'], contexts)
        self.assertFalse(request['body']['enforce_admins'])

    def test_invalid_input_never_invokes_github(self):
        for arguments in [[], ['owner/repo', 'main', 'unknown'], ['owner/repo', '../bad']]:
            result, request = self.run_helper(arguments)
            self.assertNotEqual(result.returncode, 0)
            self.assertIsNone(request)
