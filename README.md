# Commit It

[Source repository](https://github.com/sungyongcho-ops/commit-it)

A portable skill for scoped commits, authorized GitHub delivery, requested PR reviews
and explicitly assigned conflict resolution. Repository rules own permissions, roles
and records; this skill supplies the Git working procedure.

## Install

Use your product's native skill installation mechanism and its default location.
For Codex, ask its built-in skill-installer to install this repository. For Claude Code,
follow its native skills installation workflow. The former shared-directory installer
is retired; it creates no links, copies, discovery configuration or background updater.

- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)

Install/update separately from source Git maintenance. An installed skill is not an
editable Git source and publication does not silently change product installations.

## Use

Invoke `$commit-it` or the product's equivalent. Give the change or PR scope and intended
delivery. Existing authorization and repository instructions determine the next step;
an invocation without commit authority produces a preview.

- [Core workflow](SKILL.md)
- [Assigned work](references/worker-coordination.md)
- [Review and repair](references/pr-review.md)
- [Conflict resolution](references/conflict-resolution.md)

## Maintain

Edit the current Git source, preserve concurrent work and run affected verification.
Keep private host/account policy outside this public package. Follow
[release maintenance](docs/releasing.md) for versioning. There is no dependency on an
OPS snapshot, skill-source directory or a shared installation layout.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_release.py
sh -n scripts/protect-branch.sh
```
