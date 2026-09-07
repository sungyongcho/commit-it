# Commit It

A reusable agent skill for scoped GitHub delivery, explicit worker coordination,
and concise pull request reviews.

- Connect requested work, issues, commits, verification and PRs.
- Preserve foreign changes and the repository's own authority rules.
- Track worker ownership independently of shared GitHub accounts.
- Publish precise `Self-review: LGTM`, `Review: LGTM` or actionable change requests.
- Reuse valid evidence instead of repeating broad audits.

## Install

Ask your agent's skill installer to install `sungyongcho/commit-it` from GitHub.
The skill is at the repository root. Prefer an exact reviewed commit for managed use.

For a new, empty Codex skill location:

```sh
git clone https://github.com/sungyongcho/commit-it "$HOME/.codex/skills/commit-it"
```

Claude Code can use the same package at `$HOME/.claude/skills/commit-it`. Preserve
existing installations and local instructions; do not clone over or reset them.
A managed installer should copy the package files unchanged and put project-specific
policy in the project's or host's own instructions. New Codex skill installations
are available on the next turn.

## Use

Invoke `$commit-it` with the requested scope, or let the agent select it for relevant
delivery work. It does not grant permission to publish, merge, change protections,
spend money or overwrite user work. Repository and user instructions take precedence.

Start with `SKILL.md`. Read `references/worker-coordination.md` when using named
workers, and `references/pr-review.md` for review work. The optional protection helper
requires Python 3 and an authenticated GitHub CLI, and changes protection only when
you explicitly authorize that operation.

## Maintain

This repository is the canonical reusable package. Keep personal account routing,
private operations state, credentials and machine-specific settings outside it.
Consumers can vendor the five package files with an exact source commit and SHA-256
manifest. That provides a complete offline copy without a recursive submodule checkout.
Update the source first, then review and advance the consumer's pin.

Run `python3 -m unittest discover -s tests` and `sh -n scripts/protect-branch.sh`.

Created by [Sungyong Cho](https://sungyongcho.com).
