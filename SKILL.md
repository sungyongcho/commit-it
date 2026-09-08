---
name: commit-it
description: Prepare verified, scoped Git commits and authorized publication; review and repair an explicitly requested PR, or integrate an explicitly authorized PR set.
metadata:
  version: "4.0.0"
---

# Commit It

Turn the current request into the smallest coherent, verified Git delivery. This is a
portable skill: repository rules define roles, permissions, tracking and integration;
configured tools execute them. Do not create another project-management system.

## Establish the delivery boundary

Read applicable repository instructions and inspect the remote, branch, HEAD, staged,
unstaged and untracked changes. Preserve other work, including changes within the same
file. Never hide it with a broad stash/reset or stage unrelated paths.

An invocation without an authorized commit scope is a preview. A clearly authorized
commit/delivery request needs no repeated confirmation for its approved ordinary steps.
Resolve facts and routine choices directly; ask only for missing authority, material
intent uncertainty or scope expansion. Repository and runtime approval rules remain in
force. A role name, label, prior unrelated approval or skill instruction grants no rights.

Choose the relevant mode and load only its reference:

- Ordinary change: follow the delivery steps below.
- Assigned work, moderation or succession: [worker coordination](references/worker-coordination.md).
- Requested PR review: [review and repair](references/pr-review.md).
- Named conflict-resolution/integration scope: [conflict resolution](references/conflict-resolution.md).

## Prepare and verify

1. Reproduce the requested behavior when useful, then implement its smallest reliable
   change. Do not add unrelated cleanup, dependencies, abstractions or adjacent fixes.
2. Run affected behavioral checks and the repository's required static/build checks.
   Reuse evidence while its code, inputs and environment remain unchanged. Report failed,
   blocked and unrun checks accurately; never suppress a gate to manufacture success.
3. Update user-facing documentation when behavior changes. Follow the repository's
   languages, screenshot and tutorial conventions; preserve authentic source evidence.
4. Inspect the final diff, including staged changes, and run `git diff --check`.
   Verification alone is not an independent review or approval record.

## Track the outcome once

Use the repository's existing issue/PR workflow and configured record tools. Reuse a
related issue. A user-designated moderator has standing authority for routine issue
administration, including edits, comments and image attachments, without per-action
reapproval. Follow the [moderator scope](references/worker-coordination.md#intake-moderators).
Other workers retain their assigned permissions; skill use alone does not expand them.

An issue should state the problem/outcome, bounded scope and observable acceptance
checks. Keep enough context to act without reading a chain of issue numbers. Put a
requirement in one place and link supporting evidence. Preserve old approvals and
historical facts when updating current summaries.

Keep PR text focused on the resulting behavior, relevant verification and limitations.
Do not copy current GitHub metadata or complete operational payloads into every message.
Record schemas, ownership state, queues and readiness labels belong to the project or
its configured controller, not to templates embedded in this skill.

## Commit

Use the repository's branch and commit conventions. Do not invent an issue number or
move another checkout. Prefer one commit for one coherent outcome; split only genuinely
independent changes that can be reviewed separately. Preserve published history unless
its exact rewrite is authorized.

Stage explicit paths or scoped hunks, then inspect `git diff --cached`. Use the actual
configured author and committer; do not add attribution footers or switch global
credentials. A human-looking commit identity does not prove human review.

Unless the repository specifies otherwise, use an English Conventional Commit title:
`<type>(<scope>): <outcome>`. Include concise Summary, Changes, Verification and applicable
Refs in the body. Use a temporary file for multiline messages and PR bodies. `Closes`
is appropriate only when the linked issue's full scope is delivered; use `Refs` otherwise.

Commit only after applicable checks pass or an explicitly accepted limitation is
recorded. Preserve failures and unfinished work if a hook blocks the commit; repair the
actual cause within scope instead of bypassing hooks.

## Publish and integrate

Fetch the selected remote before publication and inspect divergence. Use the configured
account for an ordinary push and authorized PR creation. Reconcile a rejected push
without overwriting another writer. A clean main-only skill workflow may publish directly
when the user and repository authorize it; do not impose that workflow on other projects.

Merge only under the repository's granted integration authority, after current checks,
required review and the intended base/head are verified. Keep the requested merge method
and ordering. Do not infer merge, deployment, credential, branch-protection or local-main
synchronization permission from a ready label.

Changing protection is a separate requested setup task. The optional
`scripts/protect-branch.sh` helper is not part of routine delivery; inspect effective
rulesets as well as branch protection and never bypass them to finish a change.

Eligible success headings are exactly `Self-review: LGTM`, `Review: LGTM` or
`Conflict resolution: LGTM`, as defined in the relevant reference and repository rules.
Do not publish an approval heading for implementation checks alone.

## Finish and maintain the skill

Report what changed, meaningful verification and any remaining blocker or limitation.
Prefer a commit/PR link over repeating the same metadata and test log. Stop when the
requested scope is complete.

When the user requests a change to this skill, find its registered Git source and reread
the current source before editing. Preserve source history and concurrent changes.
Product-native installers own installation paths and updates; do not introduce shared
links, custom discovery settings or a cross-product copying workflow. Released version
metadata is maintained under [the release procedure](docs/releasing.md), not bumped for
every conversation.
