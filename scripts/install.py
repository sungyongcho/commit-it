#!/usr/bin/env python3
"""Install one Commit It source and link supported local agent discovery paths."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

MARKER = '.commit-it-install.json'


class InstallError(Exception):
    """An installation conflict that must preserve existing content."""


def package(source):
    required = ['SKILL.md', 'agents/openai.yaml', 'scripts/protect-branch.sh']
    required += [name for name in ('README.md', 'CHANGELOG.md') if (source / name).is_file()]
    names = sorted(set(required + [p.relative_to(source).as_posix()
        for area in ('references', 'scripts', 'docs') for p in (source / area).rglob('*')
        if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.md', '.py', '.sh')]))
    result = {}
    for name in names:
        p = source / name
        if not p.is_file() or any(parent.is_symlink() for parent in (p, *p.parents) if parent != source and source in parent.parents):
            raise InstallError('Missing or redirected package file: ' + name)
        result[name] = p.read_bytes()
    if not result['SKILL.md'].startswith(b'---\nname: commit-it\n'):
        raise InstallError('Invalid Commit It package.')
    return result


def hashes(data):
    return {name: hashlib.sha256(value).hexdigest() for name, value in data.items()}


def _install(source, destination, agents, update=False, dry_run=False, home=None):
    source, destination = Path(source).resolve(), Path(destination).absolute()
    home = Path(home) if home is not None else Path.home()
    data = package(source)
    # Gemini also discovers .agents/skills; share that path rather than duplicating it.
    locations = {'codex': '.agents/skills', 'claude': '.claude/skills', 'gemini': '.agents/skills'}
    targets = sorted({home / locations[agent] / 'commit-it' for agent in agents})
    legacy = [home / '.codex/skills/commit-it', home / '.gemini/skills/commit-it']
    for path in legacy:
        if (path.exists() or path.is_symlink()) and path not in targets:
            raise InstallError('Existing legacy discovery path requires reconciliation: ' + str(path))
    for path in targets:
        if (path.exists() or path.is_symlink()) and not (path.is_symlink() and path.resolve() == destination.resolve()):
            raise InstallError('Preserve the existing installation: ' + str(path))
    same_source = source == destination.resolve()
    exists = destination.exists() or destination.is_symlink()
    if destination.is_symlink():
        raise InstallError('Choose the real canonical directory, not a destination symlink.')
    old = None
    if exists and not same_source:
        marker = destination / MARKER
        if not marker.is_file() or marker.is_symlink():
            raise InstallError('Existing source is not managed by this installer.')
        old = json.loads(marker.read_text())
        actual = {p.relative_to(destination).as_posix(): p.read_bytes() for p in destination.rglob('*')
                  if p.is_file() and p.name != MARKER and '__pycache__' not in p.parts}
        if any(p.is_symlink() for p in destination.rglob('*')) or hashes(actual) != old.get('files'):
            raise InstallError('Local changes require review before update.')
        if old['files'] != hashes(data) and not update:
            raise InstallError('A different package requires --update.')
    result = {'source': str(destination), 'agents': agents, 'targets': [str(p) for p in targets],
              'files': hashes(data), 'dry_run': dry_run}
    if dry_run:
        return result
    destination.parent.mkdir(parents=True, exist_ok=True)
    changed = not same_source and (not old or old['files'] != hashes(data))
    previous = None
    created_links = []
    try:
        if changed:
            with tempfile.TemporaryDirectory(prefix='.commit-it-stage-', dir=destination.parent) as temporary:
                stage = Path(temporary) / 'commit-it'
                stage.mkdir()
                for name, content in data.items():
                    p = stage / name
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(content)
                    p.chmod(0o755 if (source / name).stat().st_mode & 0o111 else 0o644)
                revision = subprocess.run(['git', '-C', str(source), 'rev-parse', 'HEAD'], capture_output=True, text=True)
                (stage / MARKER).write_text(json.dumps({'schema': 1, 'repository': 'sungyongcho/commit-it',
                    'revision': revision.stdout.strip() if revision.returncode == 0 else None,
                    'files': hashes(data)}, indent=2) + '\n')
                if exists:
                    current = {p.relative_to(destination).as_posix(): p.read_bytes() for p in destination.rglob('*')
                               if p.is_file() and p.name != MARKER and '__pycache__' not in p.parts}
                    if any(p.is_symlink() for p in destination.rglob('*')) or hashes(current) != old['files']:
                        raise InstallError('Installation changed concurrently; preserve local work.')
                    previous = Path(temporary) / 'previous'
                    os.rename(destination, previous)
                try:
                    os.rename(stage, destination)
                    for path in targets:
                        if not path.is_symlink():
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.symlink_to(destination, target_is_directory=True)
                            created_links.append(path)
                except BaseException:
                    for path in reversed(created_links):
                        path.unlink()
                    if destination.exists():
                        shutil.rmtree(destination)
                    if previous is not None:
                        os.rename(previous, destination)
                    raise
        else:
            for path in targets:
                if not path.is_symlink():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(destination, target_is_directory=True)
                    created_links.append(path)
    except BaseException:
        for path in reversed(created_links):
            if path.is_symlink():
                path.unlink()
        raise
    result['reload'] = {'codex': 'Reload discovery or restart if needed.',
                        'claude': 'Restart if the skills directory was newly created.',
                        'gemini': 'Run /skills reload, then /skills list.'}
    result['tools'] = {name: shutil.which(name) is not None for name in ('git', 'python3', 'gh', *agents)}
    return result


def install(source, destination, agents, update=False, dry_run=False, home=None):
    if dry_run:
        return _install(source, destination, agents, update, True, home)
    user_home = Path(home) if home is not None else Path.home()
    state = user_home / '.local/state/commit-it-installer'
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / 'install.lock').open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise InstallError('Another installation is in progress.') from error
        return _install(source, destination, agents, update, False, home)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=('codex', 'claude', 'gemini', 'both', 'all'), required=True)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--destination', type=Path, default=Path.home() / 'Documents/skills/commit-it')
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    agents = ['codex', 'claude', 'gemini'] if args.agent == 'all' else ['codex', 'claude'] if args.agent == 'both' else [args.agent]
    try:
        print(json.dumps(install(args.source, args.destination, agents, args.update, args.dry_run), indent=2))
    except (InstallError, OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
