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

    def test_work_record_retains_legacy_marker_and_additive_lineage_fields(self):
        """Validate the copyable record without requiring clients to migrate v1 data."""
        text = (ROOT / 'references/worker-coordination.md').read_text()
        records = re.findall(r'```markdown\n(<!-- commit-it:work-state:v1 -->[\s\S]*?)```', text)
        self.assertEqual(len(records), 1)
        record = records[0]
        pairs = re.findall(r'^- ([^:]+): (.+)$', record, re.MULTILINE)
        fields = dict(pairs)
        self.assertEqual(len(pairs), len(fields), 'duplicate work-state field')
        self.assertTrue({'Work status', 'Worker', 'Assignment', 'Scope', 'Issues',
                         'PR', 'Verification', 'Updated'} <= fields.keys())
        self.assertEqual(fields['Previous worker'], 'worker-1')
        self.assertEqual(int(fields['Handoff revision']), 1)
        self.assertRegex(fields['Worker'], r'^codex-\d{8}T\d{6}Z-[0-9a-f]{8}$')
        self.assertIn('<!-- /commit-it:work-state -->', record)
        self.assertNotEqual(fields['Worker'], fields['Previous worker'])
        self.assertEqual(fields['Work status'], 'OCCUPIED')

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

    def test_sequence_excerpt_has_canonical_fields_and_separate_merge_states(self):
        """Keep the illustrative schema lowercase and avoid publishing a duplicate payload."""
        text, blocks = self.conflict_blocks()
        excerpts = [body for kind, body in blocks if body.startswith('### Merge sequence\n')]
        self.assertEqual(len(excerpts), 1)
        record = excerpts[0]
        pairs = re.findall(r'^- ([^:]+):([^\n]*)$', record, re.MULTILINE)
        fields = {name: value.strip() for name, value in pairs}
        self.assertEqual(len(pairs), len(fields), 'duplicate canonical field')
        self.assertEqual(set(fields), {'schema_version', 'id', 'role', 'resolver',
                                      'revision', 'status', 'order', 'prs'})
        self.assertEqual(fields['schema_version'], '2')
        self.assertEqual(fields['role'], 'conflict-resolver')
        self.assertEqual(fields['prs'], '{}')
        self.assertEqual(len(re.findall(r'^  - ', record, re.MULTILINE)), 2)
        self.assertNotIn('```json', record)
        self.assertNotIn('Work status', fields)
        states = set(re.findall(r'^\| `([A-Z_]+)` \|', text, re.MULTILINE))
        self.assertEqual(states, {'PREPARING', 'MERGE_SEQUENCE_READY', 'MERGING', 'MERGED', 'BLOCKED'})
        self.assertIn(fields['status'], states)

    def test_review_request_excerpt_has_one_public_payload(self):
        """Preserve schema keys and a current record marker without a hidden JSON shadow."""
        text = (ROOT / 'references/pr-review.md').read_text()
        excerpts = re.findall(r'```markdown\n(<!-- ops:review-request:v2:[\s\S]*?)```', text)
        self.assertEqual(len(excerpts), 1)
        pairs = re.findall(r'^- ([^:]+): (.+)$', excerpts[0], re.MULTILINE)
        fields = dict(pairs)
        self.assertEqual(len(pairs), len(fields), 'duplicate request field')
        self.assertEqual(set(fields), {'scope', 'worker', 'assignment', 'id', 'head', 'base', 'task', 'issues'})
        self.assertEqual(fields['issues'], '[]')
        self.assertIn(':v2:' + fields['id'] + ' -->', excerpts[0])
        self.assertEqual(excerpts[0].count('<!--'), 1)

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
        fields = dict(re.findall(r'^(Repository|Target PRs|Base branch|Resolver ID|Merge authorization|Review authorization|Merge method): (.+)$', prompt, re.MULTILINE))
        self.assertEqual(fields, {'Repository': '<owner/repository>', 'Target PRs': '<PR list>',
            'Base branch': '<base>', 'Resolver ID': '<actual worker ID>',
            'Merge authorization': 'granted for this named PR set',
            'Review authorization': 'user-approved resolver self-review for this named PR set',
            'Merge method': 'squash'})
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
