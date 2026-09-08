# Assigned work and continuity

Read the repository's AGENTS.md, WORKER.md and, for user-designated intake, MODERATOR.md.
They define assignment, delivery, status-record and ownership rules. Use their configured
tools and schemas; do not maintain a second record format inside this skill.

## Ownership and succession

Use the actual worker/task IDs and retain them across resumptions. An account, model,
chat title or label is not an execution owner. Before writing, verify current ownership
of the exact issue/PR/files; one writer controls overlapping work and Git publication.

A user-approved succession transfers the named scope while preserving original authors,
assignment lineage, commits, unfinished checkpoints and valid verification. Do not wait
for a vanished predecessor when the project permits direct user-directed takeover.
Reconcile actual competing writers. A replacement model neither invalidates unchanged
checks nor proves independent review.

## Delivery and review

Complete the assigned implementation under its delivery contract. REVIEW_READY, where
used, records completed implementation; it does not start a review. A separate user
review request follows [review and repair](pr-review.md). Preserve current head/base
binding, repair disclosures and the project's MERGE_READY rules. No readiness label
alone grants merging or checkout synchronization.

The eligible headings remain `Self-review: LGTM`, `Review: LGTM` and
`Conflict resolution: LGTM`. Use each only under its actual authorization. A named
resolver follows [conflict resolution](conflict-resolution.md).

## Intake and evidence

Moderators register actionable scope in the destination project's existing records,
reuse duplicates and preserve active owners. Keep held drafts in the authorized chat or
handoff surface. A user-designated single-worker epic stays whole.

Records should state the outcome, necessary decision evidence and next action once.
Preserve historical authors, approvals and reviewed SHAs. Link detailed evidence; use
current tools to retrieve current metadata. Tool or runtime refusals require accurate
reporting and an authorized resolution, never another account or tool as a bypass.
