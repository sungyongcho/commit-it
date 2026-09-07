# Commit It

A reusable skill for scoped GitHub delivery in Codex, Claude Code and Gemini CLI.
Connect requested work, issues, commits, verification and PRs while preserving foreign
changes, actual worker ownership and the repository's authority rules.

## Install

The same `SKILL.md`, references and helpers work across supported local skill loaders.
The installer keeps one source at `~/Documents/skills/commit-it` and links agent discovery
paths to it. Codex and Gemini share `~/.agents/skills/commit-it`; Claude Code uses
`~/.claude/skills/commit-it`. It does not install agent applications or change authentication.

You need Python 3 and Git. GitHub operations also require `gh` and the appropriate login.
Missing tools are reported. Use a reviewed source commit for managed installations.
A version label alone does not identify unpublished local edits.

### Codex

Copy this prompt into Codex:

```text
Install Commit It from https://github.com/sungyongcho/commit-it for Codex.
Read the current README and inspect scripts/install.py from one reviewed source commit.
Use the default shared source location and run the installer with --agent codex.
Preserve existing skills and local changes; report conflicts instead of overwriting them.
Verify the resolved source, source commit and installed files, then confirm skill discovery.
Do not install other applications, change credentials, or perform GitHub writes.
```

Or run these commands after reviewing the downloaded source:

```sh
install_source=$(mktemp -d)
git clone --depth 1 https://github.com/sungyongcho/commit-it "$install_source/commit-it"
git -C "$install_source/commit-it" rev-parse HEAD
python3 "$install_source/commit-it/scripts/install.py" --agent codex --dry-run
python3 "$install_source/commit-it/scripts/install.py" --agent codex
```

Invoke `$commit-it` with the requested scope. If discovery has not refreshed, restart
Codex. See [official local skill discovery](https://learn.chatgpt.com/docs/build-skills).

### Claude Code

Copy this prompt into Claude Code:

```text
Install Commit It from https://github.com/sungyongcho/commit-it for Claude Code.
Read the current README and inspect scripts/install.py from one reviewed source commit.
Use the default shared source location and run the installer with --agent claude.
Preserve existing skills and local changes; report conflicts instead of overwriting them.
Verify the resolved source, source commit and installed files, then confirm /commit-it discovery.
Do not install other applications, change credentials, or perform GitHub writes.
```

```sh
install_source=$(mktemp -d)
git clone --depth 1 https://github.com/sungyongcho/commit-it "$install_source/commit-it"
git -C "$install_source/commit-it" rev-parse HEAD
python3 "$install_source/commit-it/scripts/install.py" --agent claude --dry-run
python3 "$install_source/commit-it/scripts/install.py" --agent claude
```

Invoke `/commit-it` with the requested scope. Restart Claude Code if its top-level
skills directory was created during the current session. See
[official Claude Code skills](https://code.claude.com/docs/en/skills).

### Gemini CLI and shared installation

Use `--agent gemini` for Gemini, `--agent both` for Codex and Claude Code, or
`--agent all` for all three. These choices share source files rather than duplicating them.
In Gemini, run `/skills reload` and `/skills list`, then explicitly ask to use the
`commit-it` skill. See [Gemini skills](https://geminicli.com/docs/cli/using-agent-skills/).

Linux, macOS and WSL are the supported installer targets. Native Windows and cloud
sessions are outside this local installer. File registration and runtime invocation
are separate checks; missing agent executables are reported, not counted as verified.

### Updates and existing installations

Re-running an identical installation leaves its package and discovery links unchanged. To update an installer-managed copy,
review a fresh source checkout and run its installer with the same selection and
`--update`. Recorded hashes, directory inventory and modes must still match the current installation.
Every replaced managed copy remains in a retained sibling `.commit-it-backups` directory;
the JSON result names its `backup` path. No previous source is discarded after success. Extra, modified,
redirected or unmanaged files stop the update. `--dry-run` does not write files.

An editable Git source and an installer-managed release copy are different targets.
The installer refuses to copy over a Git root, even with `--update`. Maintain that source
through its configured, snapshot-guarded patch workflow and retain an exact backup; do
not replace its `.git`, local branch or local maintenance instructions with a release copy.
If the shared source is your development Git checkout, link it using its own installer:

```sh
python3 "$HOME/Documents/skills/commit-it/scripts/install.py" --agent all
```

Update that checkout through its repository workflow. Do not replace it with a downloaded
snapshot. Existing paths such as `~/.codex/skills/commit-it` require reviewed migration.
Keep backups outside skill search locations and reconcile useful local changes before
replacing directories with links. Redirected discovery or destination parent directories
also require reconciliation; the installer never writes through them. Do not blindly reset
or clone over an installation.

## Use

Start with `SKILL.md`. Follow applicable repository instructions, including `AGENTS.md`
and `CLAUDE.md`, without replacing or consolidating them during installation. Review
the concrete commit preview before authorizing execution. Loading the skill does not
authorize publication, merge, protection changes, spending or overwriting work.

Read [worker coordination](references/worker-coordination.md) for named workers and
[PR review](references/pr-review.md) for review work. Reload the real source when another
conversation may have updated it; existing context is not rewritten by filesystem changes.

### Worker succession in 3.0.0

Workers are replaceable execution owners. Project assignments, commits, PRs and tested
checkpoints preserve continuity when chats disappear or a later model takes over.
Explicit user approval transfers named work without waiting for a predecessor response;
existing IDs and v1 records remain valid. The changed transfer contract is the reason
for the major version, not an incompatible storage migration.

The coordination reference defines collision-checked IDs, assignment lineage, OPS
ownership/commit receipts, and `DEV`/`OPS` plus `OCCUPIED`/`REVIEW_READY` label synchronization.
Personal accounts still author development commits and create PRs when the repository
separates those actions from OPS records. Labels do not grant ownership or merge authority.

Conversation names follow `<short scope> | <project summary> | <short worker id>`.
Use supported official tools and verify the new title; otherwise provide the suggested
title without blocking development. Chat titles and IDs are optional lookup aids.

For an explicitly assigned resolver of a named PR set, read
[conflict resolution](references/conflict-resolution.md). Ordinary worker authority is unchanged.

## Maintain

This repository is the canonical reusable package. Keep private routing, host policy,
credentials and machine-specific settings outside it. Use one local source with links
for authoring and reviewed commit pins for distributed recovery snapshots.

Ordinary policy edits do not bump the release version. Track working changes by content
hash and Git state. Resolve pending related changes before selecting a release number.
See [release policy](docs/releasing.md) and [unreleased changes](CHANGELOG.md).

```sh
python3 -m unittest discover -s tests
sh -n scripts/protect-branch.sh
python3 scripts/check_release.py
```

Created by [Sungyong Cho](https://sungyongcho.com).

### Reviewed package inventory

`scripts/install.py` declares `PACKAGE_FILES`: `SKILL.md`, `README.md`, `CHANGELOG.md`,
`agents/openai.yaml`, the three references (`pr-review.md`, `worker-coordination.md`,
`conflict-resolution.md`), the three scripts (`protect-branch.sh`, `install.py`,
`check_release.py`), and `docs/releasing.md`. Consumer pinning can validate this fixed
list without executing an unreviewed installer. Tests, CI, `.git` and local maintenance
instructions remain in the authoring repository, outside copied release packages.
A copy records a source commit only when all packaged bytes match that repository's
HEAD; unpublished edits are not mislabeled as the committed release.
