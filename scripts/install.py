#!/usr/bin/env python3
"""Install a verified package copy or link an existing editable Commit It source."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

MARKER = '.commit-it-install.json'
PACKAGE_FILES = (
    'SKILL.md', 'README.md', 'CHANGELOG.md', 'agents/openai.yaml',
    'references/pr-review.md', 'references/worker-coordination.md',
    'references/conflict-resolution.md', 'scripts/protect-branch.sh',
    'scripts/install.py', 'scripts/check_release.py', 'docs/releasing.md',
)


class InstallError(Exception):
    """An installation conflict that must preserve existing content."""


def package(source):
    """Read the fixed public inventory without following redirected package entries."""
    source = Path(source).resolve()
    result = {}
    for name in PACKAGE_FILES:
        path = source / name
        if not path.is_file() or any(parent.is_symlink() for parent in (path, *path.parents)
                                    if parent != source and source in parent.parents):
            raise InstallError('Missing or redirected package file: ' + name)
        result[name] = path.read_bytes()
    if not result['SKILL.md'].startswith(b'---\nname: commit-it\n'):
        raise InstallError('Invalid Commit It package.')
    return result


def hashes(data):
    """Identify exact package bytes without executing their contents."""
    return {name: hashlib.sha256(value).hexdigest() for name, value in data.items()}


def _snapshot(root):
    """Include every file and directory, including caches, and refuse links or special files."""
    files, modes = {}, {}
    for path in (root, *sorted(root.rglob('*'))):
        name = '.' if path == root else path.relative_to(root).as_posix()
        if name == MARKER:
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise InstallError('Local changes include a redirected path: ' + name)
        modes[name] = stat.S_IMODE(info.st_mode)
        if stat.S_ISREG(info.st_mode):
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not stat.S_ISDIR(info.st_mode):
            raise InstallError('Local changes include a special file: ' + name)
    return {'files': files, 'modes': modes}


def _managed(root):
    """Validate a complete managed-copy record; an editable Git source is never adopted."""
    if (root / '.git').exists() or (root / '.git').is_symlink():
        raise InstallError('Preserve this editable Git source; apply a reviewed source patch instead.')
    marker = root / MARKER
    if not marker.is_file() or marker.is_symlink():
        raise InstallError('Existing source is not managed by this installer.')
    content = marker.read_bytes()
    value = json.loads(content)
    if not isinstance(value, dict) or value.get('schema') != 1 or value.get('repository') != 'sungyongcho/commit-it':
        raise InstallError('Unrecognized installation record; preserve the existing source.')
    if not isinstance(value.get('files'), dict) or not isinstance(value.get('modes'), dict):
        raise InstallError('Legacy or incomplete installation record requires explicit reconciliation.')
    snapshot = _snapshot(root)
    if snapshot != {'files': value['files'], 'modes': value['modes']}:
        raise InstallError('Local changes require review before update.')
    return value, content, snapshot


def _locations(home, agents):
    """Resolve each requested discovery path explicitly, including legacy conflicts."""
    locations = {'codex': '.agents/skills', 'claude': '.claude/skills', 'gemini': '.agents/skills'}
    if not agents or any(agent not in locations for agent in agents):
        raise InstallError('Choose supported agents: codex, claude, gemini.')
    return sorted({home / locations[agent] / 'commit-it' for agent in agents}), [
        home / '.codex/skills/commit-it', home / '.gemini/skills/commit-it']


def _no_redirected_parents(path):
    """Keep writes inside the explicitly named directory chain, never through a parent link."""
    for parent in Path(path).parents:
        if parent.is_symlink():
            raise InstallError('Redirected parent requires reconciliation: ' + str(parent))


def _discovery(targets, legacy, destination):
    """Reject foreign copies, redirected links and legacy locations without modifying them."""
    for path in legacy:
        if (path.exists() or path.is_symlink()) and path not in targets:
            raise InstallError('Existing legacy discovery path requires reconciliation: ' + str(path))
    for path in targets:
        _no_redirected_parents(path)
        if (path.exists() or path.is_symlink()) and not (
                path.is_symlink() and path.resolve() == destination.resolve()):
            raise InstallError('Preserve the existing installation: ' + str(path))


def _revision(source, data):
    """Name a source commit only when this repository root and all installed bytes match it."""
    def read(*args):
        """Read Git objects without refreshing or changing the author's checkout."""
        return subprocess.run(['git', '-C', str(source), *args], capture_output=True,
                              env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'})
    try:
        top = read('rev-parse', '--show-toplevel')
        head = read('rev-parse', 'HEAD')
        if top.returncode or head.returncode or Path(os.fsdecode(top.stdout).strip()).resolve() != source:
            return None
        revision = head.stdout.decode().strip()
        for name, content in data.items():
            blob = read('show', revision + ':' + name)
            if blob.returncode or blob.stdout != content:
                return None
        return revision
    except OSError:
        return None


def _backup_path(destination):
    """Allocate a retained sibling backup outside any temporary staging directory."""
    root = destination.parent / '.commit-it-backups'
    if root.is_symlink():
        raise InstallError('Backup directory is redirected; preserve existing content.')
    root.mkdir(mode=0o700, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=destination.name + '-', dir=root)) / 'source'


def _stage(source, stage, data, revision):
    """Write only the reviewed package inventory into a private staging tree."""
    stage.mkdir(mode=0o755)
    for name, content in data.items():
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.chmod(0o755 if (source / name).stat().st_mode & 0o111 else 0o644)
    snapshot = _snapshot(stage)
    (stage / MARKER).write_text(json.dumps({'schema': 1, 'repository': 'sungyongcho/commit-it',
        'revision': revision, **snapshot}, indent=2) + '\n')
    return snapshot


def _install(source, destination, agents, update=False, dry_run=False, home=None):
    """Preflight all state, then copy a release or link an unchanged authoring source."""
    source, destination = Path(source).resolve(), Path(destination).absolute()
    home = Path(home) if home is not None else Path.home()
    _no_redirected_parents(destination)
    data = package(source)
    targets, legacy = _locations(home, agents)
    _discovery(targets, legacy, destination)
    same_source = source == destination.resolve()
    exists = destination.exists() or destination.is_symlink()
    if destination.is_symlink():
        raise InstallError('Choose the real canonical directory, not a destination symlink.')
    old, old_bytes, old_snapshot = None, None, None
    if exists and not same_source:
        old, old_bytes, old_snapshot = _managed(destination)
        if old['files'] != hashes(data) and not update:
            raise InstallError('A different package requires --update.')
    result = {'source': str(destination), 'package_source': str(source), 'agents': agents,
              'targets': [str(path) for path in targets], 'files': hashes(data),
              'dry_run': dry_run, 'backup': None, 'mode': 'source-links' if same_source else 'managed-copy'}
    if dry_run:
        return result
    changed = not same_source and (not old or old['files'] != hashes(data))
    backup, installed, staged_snapshot = None, False, None
    created_links = []
    try:
        if changed:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.commit-it-stage-', dir=destination.parent) as temporary:
                stage = Path(temporary) / 'commit-it'
                staged_snapshot = _stage(source, stage, data, _revision(source, data))
                _no_redirected_parents(destination)
                _discovery(targets, legacy, destination)
                if exists:
                    current, marker_bytes, current_snapshot = _managed(destination)
                    if marker_bytes != old_bytes or current_snapshot != old_snapshot:
                        raise InstallError('Installation changed concurrently; preserve local work.')
                    backup = _backup_path(destination)
                    os.rename(destination, backup)
                    result['backup'] = str(backup)
                elif destination.exists() or destination.is_symlink():
                    raise InstallError('Installation appeared concurrently; preserve local work.')
                os.rename(stage, destination)
                installed = True
        _discovery(targets, legacy, destination)
        for path in targets:
            _discovery(targets, legacy, destination)
            if not path.is_symlink():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(destination, target_is_directory=True)
                created_links.append((path, path.lstat().st_ino))
        _discovery(targets, legacy, destination)
    except BaseException as error:
        for path, inode in reversed(created_links):
            if path.is_symlink() and path.lstat().st_ino == inode and path.resolve() == destination.resolve():
                path.unlink()
        if backup is not None or installed:
            try:
                if installed:
                    _, _, current = _managed(destination)
                    if current != staged_snapshot:
                        raise InstallError('New installation changed; leave it and the retained backup intact.')
                    failed = _backup_path(destination)
                    os.rename(destination, failed)
                if backup is not None:
                    # The original remains retained even when restoring its working copy.
                    shutil.copytree(backup, destination, symlinks=True)
            except BaseException as recovery:
                raise InstallError(f'Installation failed and recovery needs inspection. Retained backup: {backup}. {recovery}') from error
        raise
    result['reload'] = {'codex': 'Reload discovery or restart if needed.',
                        'claude': 'Restart if the skills directory was newly created.',
                        'gemini': 'Run /skills reload, then /skills list.'}
    result['tools'] = {name: shutil.which(name) is not None for name in ('git', 'python3', 'gh', *agents)}
    return result


def install(source, destination, agents, update=False, dry_run=False, home=None):
    """Serialize this user's requested installation; dry-run never creates state or links."""
    if dry_run:
        return _install(source, destination, agents, update, True, home)
    user_home = Path(home) if home is not None else Path.home()
    state = user_home / '.local/state/commit-it-installer'
    _no_redirected_parents(state / 'install.lock')
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / 'install.lock').open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise InstallError('Another installation is in progress.') from error
        return _install(source, destination, agents, update, False, home)


def main():
    """Expose explicit source, discovery selection, preview and managed-update controls."""
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
