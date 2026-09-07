#!/usr/bin/env python3
"""Validate release metadata and an optional proposed tag without publishing."""
import argparse
from pathlib import Path
import re


def check(root, tag=None):
    skill = (root / 'SKILL.md').read_text()
    matches = re.findall(r'^  version: "((?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*))"$', skill, re.M)
    if len(matches) != 1:
        raise ValueError('Expected one stable semantic version in skill metadata.')
    version = matches[0]
    changelog = (root / 'CHANGELOG.md').read_text()
    if '## Unreleased\n' not in changelog:
        raise ValueError('Missing Unreleased section.')
    if tag is not None:
        if tag != 'v' + version:
            raise ValueError('Proposed tag does not match skill metadata.')
        if not re.search(r'^## (?:\[)?' + re.escape(version) + r'(?:\])? - \d{4}-\d{2}-\d{2}$', changelog, re.M):
            raise ValueError('Missing dated changelog section for the proposed release.')
    return version


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag')
    args = parser.parse_args()
    try:
        print('Release metadata valid: ' + check(Path(__file__).resolve().parents[1], args.tag))
    except ValueError as error:
        parser.exit(1, str(error) + '\n')
