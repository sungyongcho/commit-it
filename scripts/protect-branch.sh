#!/bin/sh
# Apply only an explicitly authorized branch-protection profile.
set -eu
if [ "$#" -lt 2 ]; then
  printf '%s\n' 'Usage: protect-branch.sh owner/repo branch [secure|fast] [check-context ...]' >&2
  exit 2
fi
repo=$1
branch=$2
shift 2
profile=${1:-secure}
if [ "$#" -gt 0 ]; then shift; fi
exec python3 - "$repo" "$branch" "$profile" "$@" <<'PYCODE'
import json
import re
import subprocess
import sys
from urllib.parse import quote

repo, branch, profile, *contexts = sys.argv[1:]
if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
    raise SystemExit('Expected owner/repository.')
if profile not in ('secure', 'fast'):
    raise SystemExit('Unknown profile: use secure or fast.')
valid = subprocess.run(['git', 'check-ref-format', '--branch', branch], capture_output=True)
if valid.returncode:
    raise SystemExit('Invalid branch name.')
secure = profile == 'secure'
body = {'required_status_checks': {'strict': secure, 'contexts': contexts},
        'enforce_admins': secure, 'required_pull_request_reviews': {'required_approving_review_count': 0},
        'restrictions': None, 'allow_force_pushes': False, 'allow_deletions': False,
        'required_conversation_resolution': secure}
query = r'"protected: checks=\(.required_status_checks.contexts) strict=\(.required_status_checks.strict) admins=\(.enforce_admins.enabled)"'
result = subprocess.run(['gh', 'api', '--method', 'PUT', 'repos/' + repo + '/branches/' + quote(branch, safe='') + '/protection',
                         '--input', '-', '--jq', query], input=json.dumps(body), text=True)
raise SystemExit(result.returncode)
PYCODE
