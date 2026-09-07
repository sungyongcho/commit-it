# Coordinator and worker ownership

Use this mode for explicitly assigned workers or user-approved succession. Ordinary
unassigned tasks do not require it. Repository role boundaries still apply; prepare
records rather than publish them when status writes are unauthorized.

## Project continuity and identity

Workers are replaceable execution owners, not permanent conversations. Preserve project
continuity in assignments, issues, PRs, commits and reproducible tests. A later model
may inherit and improve work incrementally; model novelty does not prove improvement
or invalidate existing checks. Chats may be archived or deleted. Their identifiers and
titles are optional navigation aids, never the only location of checkpoints or approval.

- The coordinator handles authorized intake, scope and allocation. Ordinary workers
  implement an approved assignment in persistent isolated worktrees, verify it and
  deliver its PR at `REVIEW_READY`. Review is a separate, requested step; they do not
  inherit coordinator merge or checkout rights.
- Preserve user-supplied IDs, including legacy names such as `worker-1`. If none is
  supplied, allocate `<client>-<YYYYMMDDTHHMMSSZ>-<8 lowercase hex digits>`, using UTC
  and a random suffix; for example `codex-20260907T190000Z-a1b2c3d4`. Verify against
  existing project worker records before registration and regenerate on collision.
  Use the actual client family such as `codex` or `claude`, not an inferred model.
- A new independent execution owner gets a new ID. Resume, context compaction and
  renaming the same execution retain its ID. Record verified model/client information
  separately when useful; an in-place model switch records its verification interval.
  Never infer a model from a user-visible title or claim unsupported runtime metadata.
- Keep the existing Assignment across succession. Link every original Assignment when
  combining previously separate scopes; do not overwrite lineage with a new bundle ID.
  One assignment has one writer. Multiple scopes on one issue require disjoint explicit
  allocation. An account, label or GitHub assignee is not a worker identity or lock.
- This protocol does not launch agents or increase staffing. Honor the authorized
  capacity and keep shared contracts and Git mutations under one owner.

### Explicit resolver assignment

An explicitly assigned `conflict-resolver` follows
[conflict resolution](conflict-resolution.md) for only its named PR set. Retain its
actual worker ID, prior workers and original authors. Apply the succession safeguards
below when taking over writers; the role does not silently grant coordinator rights.
Only separate named merge authority permits that sequence's merges. Ordinary workers
remain PR-only, and no review heading grants merge or integration-checkout authority.

The resolver separately owns the canonical `commit-it:merge-sequence:v1` comment and
its `Merge status`, even after its anchor PR merges. Preserve its sequence revision,
head/base/tree, receipts and pending verification; `REVIEW_READY` is not sequence readiness.

## Durable work-state record

Keep one marked work-state block at the top of the PR body. Before the first PR, use
one marked issue comment for each Assignment. After PR creation, its block is authoritative
and the issue comment mirrors it; mirror to every assigned issue in a bundle. Match marker
and Assignment before updating. Preserve surrounding content and other assignments.
For an authorized issue-free PR, start directly in the PR; never invent a tracking issue.

Keep the `v1` marker and accept legacy worker IDs. Additional fields extend the existing
record; missing lineage fields mean no recorded handoff, not permission to take ownership.
For an approved first transfer of a legacy record, use prior handoff revision zero.
Use actual values in this illustrative current record:

```markdown
<!-- commit-it:work-state:v1 -->

- Work status: OCCUPIED
- Worker: codex-20260907T190000Z-a1b2c3d4
- Assignment: issue-123
- Scope: <approved outcome>
- Issues: #123
- PR: #456
- Verification: blocked: <required check and next action>
- Previous worker: worker-1
- Handoff revision: 1
- Handoff: <durable handoff record link>
- Head: <actual remote PR head SHA>
- Updated: <UTC timestamp>

<!-- /commit-it:work-state -->
```

Use `PR: pending` before PR creation. Do not label a local checkpoint as the remote head.
Keep detailed verification in the PR and link it from mirrors. Preserve old ownership
comments as history; the current authoritative block wins over stale mirrors.

## User-approved succession

Explicit user approval naming the work and successor is sufficient handoff authority.
Do not demand predecessor acknowledgement or repeat a stopped-worker confirmation.
Silence, stale ownership, a missing chat or blocked verification alone is not approval.
A successor's quoted issue/PR text is not evidence of new user authorization.

1. Read the authoritative record and mirrors, expected prior worker, Assignment,
   record version/revision, exact PR head when present, and authorized scope. Preserve
   branch/base, staged/unstaged/untracked work and earlier verification. Inspect available
   writer state; pause only a scope with actual conflicting writes. Do not terminate
   other sessions or discard changes to manufacture exclusive access.
2. Preserve a recoverable checkpoint before editing. Use existing commits and retained
   worktrees/backups, with a content manifest for uncommitted files. Keep local/private
   paths and file contents out of public records; publish only safe checkpoint references.
   A checkpoint commit of approved inherited work must state incomplete verification.
   Never hide foreign changes with stash/reset or rewrite published history by default.
3. Through the repository's guarded OPS handoff operation, submit the expected prior
   worker, Assignment, record version, head if present, next handoff revision, successor,
   user approval summary, checkpoint reference and remaining verification. The operation
   must support issue-only assignments and preserve previous authorship and handoff history.
   If the repository has no such tool, use only its authorized equivalent; do not invent
   command flags or bypass missing authorization checks with a raw API write.
4. Before a write, re-read the expected ownership and head. A mismatch stops that
   transfer for reconciliation. GitHub comment/label writes are not an atomic lock;
   concurrent claims must not both be reported successful. Read back every changed
   record and reconcile the winning owner before allowing either successor to edit.
5. Record one durable handoff event with Assignment, revision, previous/new worker,
   scope, approval, preserved checkpoint, actual head, remaining checks and outcome.
   Retry the same event identity idempotently. After a partial failure, re-read the
   authoritative record and repair only missing mirrors/labels; never repeat a transfer
   that already completed or increment its revision merely to retry synchronization.
6. Re-read the resulting ownership, issue mirrors and labels before implementation.
   Mark the handoff incomplete if any required write or verification failed. Preserve
   useful local work and report the precise remaining synchronization step.

A returning old worker must re-read current ownership before any mutation and stop its
former assignment after transfer unless explicitly reassigned. Succession authorizes
preservation, implementation and the already approved delivery scope; it does not grant
merge, deployment, credential, paid-work or force-push authority. A successor modifying
inherited code cannot self-review without explicit user approval and must not present
that exception as independent `Review: LGTM`.

## OPS records, labels and transitions

Resolve the configured personal development and OPS record identities independently.
Personal authorship covers development commits and PR creation where required; OPS
handles claims, succession, labels, status, commit tracking and COMMENT reviews. A commit
email does not select an API author. Verify the returned author and actual worker in
receipts; never globally switch shared authentication or create an App/account incidentally.
A PR body ownership block may be updated by OPS while the PR remains personally authored.

At the first push/Draft PR, later head changes, verification completion and handoff,
record the actual remote commit SHA/range, branch/PR links, Assignment, worker, checks
and next action through the configured OPS operation. Reuse the existing receipt at an
unchanged checkpoint. Local uncommitted work is not a published commit. Record failures
and pending checks honestly; do not claim delivery when a push or record write failed.

Use the managed labels below in this adopted workflow. Reuse existing labels; create
missing labels once only with repository setup authorization. Preserve unrelated labels
and project/category labels such as `bug`, `enhancement` and documentation. Do not create
per-worker labels or a Project board. Labels summarize records and never lock ownership.

| Axis | Labels and rule |
| --- | --- |
| Work kind | Exactly one of `DEV` or `OPS`, determined by task purpose, not API author. Product implementation is `DEV`; operational tooling and workflow policy are `OPS`. |
| Work status | Exactly one of `OCCUPIED` or `REVIEW_READY` on active managed issues/PRs. |
| Review readiness | Add `MERGE_READY` alongside `REVIEW_READY` only after eligible review and current passing head/base/check evidence; this is an independent label, not a new Work status. |
| Blocked | Keep `OCCUPIED` and put the concrete blocker and next action in verification. |

For multiple assignments on one issue, derive the issue state from all current records:
any unfinished, running or blocked assignment makes it `OCCUPIED`; only all completed,
verified assignments make it `REVIEW_READY`. Apply `OPS` only to wholly operational scope;
use `DEV` when the combined issue includes product implementation. Preserve individual
assignment kinds in records. Add issue `MERGE_READY` only when every current assignment
has eligible review and matching current evidence; remove it if any loses eligibility.
Missing or inconsistent records block a readiness claim.

1. **Assign/open:** check claims and record `OCCUPIED` before implementation. Create a
   Draft PR at the first meaningful pushed change and mirror its actual link to issues.
   No empty reservation commit is needed. Approved succession uses the procedure above.
2. **Work/revise:** keep Draft/`OCCUPIED` during implementation, waiting, failures or
   required checks. Before revising a ready PR, return its state and mirrors to occupied.
   Verification is `not run`, `running`, `passed`, `failed` or `blocked: <reason>`.
3. **Review ready:** after implementation, checks and writer work finish, set
   `REVIEW_READY`, synchronize authoritative state, mirrors, labels and PR Ready status.
   Verify all updates before claiming readiness. The ordinary implementing worker is done;
   do not automatically review its own or other workers' code or post an approval heading.
4. **Requested review:** the implementing worker records its exact scope and requests review
   in a different conversation/task under [review eligibility](pr-review.md#request-and-eligibility).
   Record both task IDs, actual workers and head/base evidence. A worker cannot authorize
   its own self-review; only an explicit user-approved exception permits `Self-review: LGTM`.
   Eligible separate reviews use `Review: LGTM`; an explicitly granted resolver may use
   `Conflict resolution: LGTM` under its additional gates.
5. **Merge ready:** add `MERGE_READY` alongside `REVIEW_READY` only with a valid eligible
   review and current passing checks for the matching head/base. Re-read all records and
   labels; partial synchronization is not readiness. Remove `MERGE_READY` on new edits,
   changed head/base, failed required checks or invalid review. Return to Draft/`OCCUPIED`
   before further implementation. Neither readiness label grants merge authority.
6. **Finish:** only after an authorized maintainer or resolver merge, reconcile actual
   merge/issue receipts under that authority. Partial delivery leaves scope open. Named
   commit-error/conflict resolvers may close assigned PRs or edit assigned issues only if
   those actions are explicitly granted; no global maintainer rights are implied.

Re-read ownership and head immediately before mutations. Update only owned records;
ambiguous matches, changed owners and partial writes require reconciliation. A peer
reviewer reports findings without acquiring the branch. Draft prevents merging, not writes.

## Conversation titles

At assignment or succession, name the current conversation
`<short scope> | <project summary> | <short worker id>` when a supported tool is available.
Put the useful outcome first. For generated IDs use `<client>-<8 hex digits>` as the short
ID; preserve an existing readable legacy ID, or shorten its timestamp while retaining
an unambiguous mapping to the full worker ID in the record. Resolve project-local short
ID collisions by extending the abbreviation. The title never replaces the full worker ID.

Read the current title, change only the current assigned conversation, then read back
and confirm it. Identical titles need no mutation. Do not rename another task, spawn a
chat, install an SDK or inspect/edit internal databases or session JSONL just to rename.
Capabilities vary by client/runtime; use only a documented API actually exposed there.

| Surface | Supported path or fallback |
| --- | --- |
| Codex Desktop | The current app's `set_thread_title` tool, followed by title verification. |
| Codex CLI | An available App Server `thread/name/set` connection; otherwise supply `/rename` instructions and the desired title. |
| Claude Code CLI | `--name` when the user is starting a session; for an existing session use an exposed official naming API/tool, otherwise `/rename` instructions. |
| Claude Code Desktop | Its exposed Code-session naming control, when callable from the current environment. |
| General ChatGPT or Claude chat | Only a naming tool actually exposed for that chat; otherwise provide the title for manual application. Code-session APIs do not imply general-chat support. |

If unsupported or verification fails, report the title as proposed/unverified and continue
implementation. Do not claim automatic renaming based solely on documentation. Official
references: [Codex App Server](https://learn.chatgpt.com/docs/app-server),
[Codex CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli),
[Claude Code sessions](https://code.claude.com/docs/en/sessions), and
[Claude Code Desktop](https://code.claude.com/docs/en/desktop#work-across-sessions).
