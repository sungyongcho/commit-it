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

    def test_package_excludes_private_operations_configuration(self):
        for file in [ROOT / 'SKILL.md', *ROOT.joinpath('references').glob('*.md'), ROOT / 'agents/openai.yaml']:
            text = file.read_text()
            for private in ('/home/', '/Users/', 'Documents/', 'ops:global-policy', '-----BEGIN PRIVATE KEY-----'):
                self.assertNotIn(private, text, str(file))
            self.assertNotRegex(text, r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', str(file))
            self.assertNotRegex(text, r'https://github\.com/(?!<)[A-Za-z0-9_.-]+/', str(file))

    def conflict_blocks(self):
        """Read reusable Markdown examples as data, without executing any instructions."""
        text = (ROOT / 'references/conflict-resolution.md').read_text()
        return text, re.findall(r'```([^\n]*)\n([\s\S]*?)```', text)

    def test_resolver_protocol_is_reachable_and_review_headings_are_complete(self):
        expected = {'Self-review: LGTM', 'Review: LGTM', 'Conflict resolution: LGTM'}
        for relative in ('SKILL.md', 'references/pr-review.md', 'references/worker-coordination.md'):
            text = (ROOT / relative).read_text()
            self.assertIn('conflict-resolution.md)', text, relative)
            headings = set(re.findall(r'`((?:Self-review|Review|Conflict resolution): LGTM)`', text))
            self.assertEqual(headings, expected, relative)
            self.assertNotIn('either approval label', text, relative)
        review = (ROOT / 'references/pr-review.md').read_text()
        row = next(line for line in review.splitlines() if line.startswith('| `Conflict resolution: LGTM`'))
        self.assertIn('explicitly assigned `conflict-resolver`', row)

    def test_sequence_record_carries_snapshot_receipts_and_separate_merge_states(self):
        text, blocks = self.conflict_blocks()
        records = [body for kind, body in blocks if body.startswith('<!-- commit-it:merge-sequence:v1 -->')]
        self.assertEqual(len(records), 1)
        record = records[0]
        fields = re.findall(r'^- ([^:]+): (.+)$', record, re.MULTILINE)
        self.assertEqual(len(fields), len(dict(fields)), 'duplicate sequence record field')
        self.assertEqual(set(dict(fields)), {'Sequence', 'Revision', 'Role', 'Resolver',
            'Merge status', 'Base', 'Order', 'Completed', 'Next', 'Readiness scope', 'Ready PR', 'Pending verification', 'Authorization', 'Resume', 'Updated'})
        self.assertEqual(dict(fields)['Role'], 'conflict-resolver')
        self.assertNotIn('Work status', dict(fields))
        self.assertIn('| PR | Head | Expected base | Verified tree | Evidence |', record)
        self.assertIn('<!-- /commit-it:merge-sequence -->', record)
        states = set(re.findall(r'^\| `([A-Z_]+)` \|', text, re.MULTILINE))
        self.assertEqual(states, {'PREPARING', 'MERGE_SEQUENCE_READY', 'MERGING', 'MERGED', 'BLOCKED'})
        self.assertIn(dict(fields)['Merge status'], states)

    def test_resolution_commit_example_preserves_exact_user_metadata_fields(self):
        _, blocks = self.conflict_blocks()
        examples = [body for kind, body in blocks if body.startswith('Integration-Mode:')]
        self.assertEqual(len(examples), 1)
        fields = [line.split(': ', 1) for line in examples[0].strip().splitlines()]
        self.assertTrue(all(len(field) == 2 and field[1].strip() for field in fields))
        self.assertEqual([field[0] for field in fields], ['Integration-Mode', 'Resolver',
            'Merge-Sequence', 'Sequence-Revision', 'Commit-Step', 'Merge-Order', 'Current-PR',
            'Depends-On', 'Next-PR', 'Verified-Tree'])
        self.assertEqual(dict(fields)['Integration-Mode'], 'conflict-resolution')
        self.assertNotIn('Head', dict(fields), 'future commit identity belongs in the external record')
        self.assertTrue(all(not value.startswith(('git ', 'sh ', 'eval ')) for _, value in fields))

    def test_copyable_prompt_requires_named_authority_and_keeps_launcher_settings_outside(self):
        text, blocks = self.conflict_blocks()
        prompts = [body for kind, body in blocks if body.startswith('Use $commit-it in conflict-resolution mode.')]
        self.assertEqual(len(prompts), 1)
        prompt = prompts[0]
        fields = dict(re.findall(r'^(Repository|Target PRs|Base branch|Resolver ID|Merge authorization|Merge method): (.+)$', prompt, re.MULTILINE))
        self.assertEqual(fields, {'Repository': '<owner/repository>', 'Target PRs': '<PR list>',
            'Base branch': '<base>', 'Resolver ID': '<actual worker ID>',
            'Merge authorization': 'granted for this named PR set', 'Merge method': 'squash'})
        self.assertNotIn('gpt-6-astra', prompt)
        self.assertIn('model `gpt-6-astra`, reasoning effort\n`high`', text.replace(prompt, ''))
        self.assertIn('On resume, reconcile live state and never repeat an already completed merge.', prompt)
        self.assertTrue(prompt.rstrip().endswith('while preserving required Korean product documentation.'))

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
