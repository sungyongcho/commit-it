# Coordinator and worker ownership

Use this mode when the user explicitly adopts a coordinator plus named execution
workers. Ordinary tasks do not require this protocol. Repository role boundaries
still apply; prepare a record rather than publish it if status writes are unauthorized.

## Roles and identity

- The coordinator handles issue intake/scope, assigns work and normally performs
  authorized merges or integration-checkout synchronization. Fetch and fast-forward
  a stable main when possible; do not rewrite main just because a request says rebase.
  Published-history rewrites and foreign checkout changes require explicit authority.
- Workers implement their approved assignment in isolated persistent worktrees,
  verify it, publish/update its PR and provide the review result. The user assigns
  stable IDs such as `worker-1`; retain the same ID across the assignment. Ask for a
  missing ID before publishing ownership. Never allocate another worker's identity.
- An assignment has one writer. Multiple scopes on one issue need an explicit,
  disjoint coordinator allocation. A bundle of issues shares one assignment ID.
  Shared account authorship, issue assignees and PR labels do not identify a worker.
  The user determines these workers and their count; this mode does not automatically
  spawn tasks or give subagents separate worker identities.

### Explicit resolver assignment

The user may assign role `conflict-resolver` for a named PR set under
[conflict resolution](conflict-resolution.md). Preserve the actual worker ID, source
authors and earlier worker history; the role does not create a new identity or confer
coordinator authority. Confirm stopped writers and the authorized assignment before
branch edits. An explicitly authorized resolver may merge that set, but ordinary
workers remain PR-only and a review heading never grants merge or checkout-sync rights.

Keep the existing `Work status` transitions below. The resolver separately owns the
canonical `commit-it:merge-sequence:v1` comment and its `Merge status`, including after
the anchor PR merges. Update only records within the explicit assignment and preserve
original authorship/history. Sequence readiness requires verified head/base/tree and
check evidence; it is not interchangeable with one PR's `REVIEW_READY` state.

## Current record

Keep one marked work-state block at the top of the PR body. Before the first PR,
keep the claim in one marked issue comment for the assignment. After PR creation,
the PR block is authoritative and that issue comment is its mirror. For a bundle,
mirror it to every assigned issue. Match both marker and assignment before updating;
never replace the entire issue body or another assignment's comment. For an authorized
issue-free PR, start its record directly in the PR; do not invent a tracking issue.

Illustrative record; use actual IDs, links, scope, timestamps and evidence:

```markdown
<!-- commit-it:work-state:v1 -->

- Work status: OCCUPIED
- Worker: worker-1
- Assignment: issue-123
- Scope: <approved outcome>
- Issues: #123
- PR: #456
- Verification: blocked: <required check and next action>
- Updated: <UTC timestamp>

<!-- /commit-it:work-state -->
```

The issue therefore shows who occupies the work and which PR carries it. Use
`PR: pending` until an actual PR exists. Add the branch/task reference when it is
known and useful. Put detailed test evidence in the PR rather than copying logs
into every mirror. Other ownership comments outside the marked work-state record are
historical evidence, not the current assignment or an invitation to take over.

## Transitions

1. **Assign:** the coordinator authorizes the worker ID and exact scope. The
   authorized record writer checks existing claims and records `OCCUPIED` before
   implementation. If an active owner conflicts, stop that scope for coordination.
   Labels are not an atomic claim mechanism; workers do not race to claim a backlog.
2. **Open:** at the first meaningful pushed change, create a Draft PR with the record
   and linked issues, then fill its actual PR link into the issue mirrors. Do not
   manufacture empty commits merely to create a reservation PR.
3. **Work:** keep `OCCUPIED` while running, waiting or blocked. Track verification
   separately as `not run`, `running`, `passed` or `blocked: <reason>`; a failed
   required check cannot be reported as passed. Blocking does not release the owner.
4. **Ready:** after scope and required checks are complete and writers have stopped,
   set `REVIEW_READY`, update the issue mirrors and mark the PR Ready for review.
   Include the reviewed head and reusable evidence in `Self-review: LGTM`; an explicitly
   assigned resolver uses `Conflict resolution: LGTM` only after the additional
   integration checks. Readiness alone never permits edits by a different worker.
5. **Revise:** before new implementation, return to Draft and `OCCUPIED`, update
   mirrors, then edit. An existing review applies only to its recorded head. Ordinary
   peer reviews use `Review: LGTM` for another worker's completed work or a concrete
   change request; the explicitly assigned resolver follows its integration heading.
6. **Handoff/finish:** only the coordinator explicitly reassigns after the old owner
   stops writers and preserves its checkpoint/backups. Silence, stale records,
   absent mirrors and blocked verification never imply release. After an authorized
   merge, the coordinator reconciles the linked issue record with the real outcome;
   partial delivery leaves the remaining scope open.

Re-read the owner and current head immediately before mutations. Update only the
owned record and preserve surrounding PR content. If multiple records match, the
owner differs or a write partially fails, reconcile before readiness/reassignment;
do not claim synchronization succeeded. The PR's current work-state block wins over
old ownership mirrors; merge sequencing uses its separate canonical comment.
Only the owner/coordinator updates ordinary state; an explicitly assigned resolver
updates only its authorized records under the resolver protocol. A reviewer reports
findings without taking over the branch. GitHub's Draft stage prevents merging, not concurrent file edits.

Use existing project labels/Projects only when configured. Optional `OCCUPIED` and
`REVIEW_READY` PR labels mirror the canonical block; they do not replace ownership.
Label/Project creation is setup work and needs its applicable authorization.

## Authorship

Git commit name/email and GitHub API identity are separate. Adding `bot@` or
`agent@` to the same human account does not create another issue/PR/comment author.
Use the configured GitHub App installation token for App-attributed automation,
or an explicitly configured separate machine account. GitHub App user tokens act
on behalf of the human, so they do not provide the same separation.

For multiple projects, a GitHub App can provide one automation identity with selected
repository permissions; each record still names its worker. Human review/merge uses
the human's credentials. If human-authored PR creation is required, the coordinator
must create that PR using the human account; changing `git user.email` is insufficient.
Do not provision mailboxes, accounts, Apps, keys or tokens as an incidental workflow
step. Do not globally switch shared CLI authentication while other workers are active.
