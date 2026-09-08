# Focused Pull Request Reviews

Ordinary worker reviews are off by default. REVIEW_READY completes implementation.
The user may open a separate task and explicitly request review of the named PR, or the
implementing worker may record a review request. A ready label or tracking opt-in alone
is not a request. The separate reviewer fixes clear defects within that implementation
scope on the same PR, verifies the final head/base and records MERGE_READY. Do not review
unrelated work, start a monitor or invent new implementation scope.

An explicit user review request grants standing authority for that PR's in-scope review,
repair, verification, personal commits, ordinary push, guarded rebase/expected-SHA lease
publication and user-visible task/OPS coordination through MERGE_READY. Do not ask again
for those routine actions. Repository and higher-priority runtime/tool approval policies
still apply; this document cannot override a tool restriction or missing runtime permission.
It grants no implicit merge, issue-scope edit, user-main update, credentials or deployment rights.

## Request and eligibility

- Preserve a durable request with its origin and authorization evidence, implementing worker,
  Assignment, PR, implementation task identifier, scope, exact head/base and existing checks.
  For an explicit user request, the reviewer may register the user-origin request itself;
  no additional implementing-worker request is needed. Keep the request's user origin separate
  from original implementation provenance; never claim the reviewer was the original worker.
  The reviewer records a different task identifier and its actual worker ID. A new model
  or ID in the same task is not a separate review. If task identity cannot be established,
  leave review pending instead of asserting separation. Missing chat history does not
  block ordinary user-approved succession; only review eligibility needs this evidence.
- The implementing worker may request review but may not waive separation or authorize
  its own self-review. Only explicit user approval for the named self-review permits that
  exception. Record the approval and mark the result as self-review, never independent
  or human approval. An implementation successor has the same restriction. A separate
  requested reviewer may contribute bounded repairs under the protocol below; retain
  original-request provenance and disclose its contribution instead of treating it as
  the original worker's self-approved review.
- A named commit-error or conflict resolver follows its explicit action/scope grant in
  [conflict resolution](conflict-resolution.md); a role name alone does not grant self-review.
- Use the configured guarded review request/publication operation where available. Check
  current owner, task separation or explicit exception, scope and head/base before writing.
  A request is not permission to create a new task if the runtime requires user authorization.

## Review and repair

1. Resolve the request, original implementation worker/task, assigned PR, expected
   head/base, acceptance scope and existing checks. Inspect only the changed behavior and
   direct contracts/callers; no unrelated audit is authorized.
2. Correct clear, reproducible implementation-scope defects directly. Before any edit,
   declare the bounded repair scope/files and expected head/base in the OPS record,
   preserve changes and use the same PR branch. A verified ready/paused scope needs no
   predecessor acknowledgement or another user confirmation. Use the authorized user-visible
   task messages and OPS records to coordinate pause/resume within this reviewed PR; actual
   overlapping writers block repair. Set Draft/`OCCUPIED` and remove `MERGE_READY`. Re-read
   the claim and head/base immediately before writing; reconcile drift before continuing.
   If the runtime rejects only an optional notification message, report it as unsent and
   continue only when exclusive write ownership and every required OPS record are already
   verified. If it rejects required coordination or a required record, stop the affected
   stage. Never bypass a rejection or retry the rejected action indirectly through another
   tool/account/channel; higher-priority runtime restrictions remain binding.
3. Make the smallest coherent fix and meaningful regression test. Personal identity
   authors/commits/pushes the repair to the same PR; OPS records original author/request,
   reviewer-as-contributor, claimed files, repair commits and resulting head. Preserve
   authorship/provenance and a recoverable checkpoint. Apply only the guarded rebase/lease
   exception below; do not create a replacement PR, merge, edit issue scope or acquire
   unrelated ownership merely because review was requested.
4. Rebase the reviewed branch onto its current base before final readiness under the protocol
   below. Reuse valid prior tests; rerun affected checks after corrections and verify the final
   PR head/base and accepted implementation scope. Pending CI remains pending. Record
   the actual repair range and state explicitly that the reviewer contributed corrections
   and is not an independent reviewer of those corrections. This remains `Review: LGTM`
   when the separate requested-review contract is satisfied; a new ID alone cannot create
   that eligibility. Original implementation workers still need explicit user approval
   for ordinary self-review.
5. For complex intent, material scope changes, unclear correction direction or missing
   authority, leave only the affected unit blocked with a focused question/change request
   and preserve completed fixes. Do not invent extra requirements or use optional style
   preferences as blockers. A fixable, clear in-scope defect should not be returned merely
   as instructions for the original worker to implement.
6. Publish the eligible result through the guarded OPS operation for the final head/base.
   Use COMMENT when formal review approval is unsupported; a transport choice cannot
   bypass eligibility. Return verified work to Ready/`REVIEW_READY` and add `MERGE_READY`
   only after review, current checks and synchronized records pass. Release the temporary
   repair claim without losing original ownership or contribution history. Neither ready
   label grants automatic merge, deployment or main synchronization.

For unresolved findings, identify the actual issue, exact file/current diff line, trigger,
observed versus expected result and the decision/recheck required. Keep the review within
the implementation's acceptance scope. Link detailed evidence, do not copy whole logs.
Public request, repair and review receipts follow the
[canonical Markdown contract](worker-coordination.md#public-record-format), with each field
once and no public JSON payload. Machine-readable data and human summaries must not diverge.

Implementation ends with verified `REVIEW_READY` delivery and no approval heading.
For an eligible review, reuse the implementation and tester's passing evidence; inspect
the requested delta and rerun checks only for a relevant change or failure. An unfinished
scope, known blocker or pending required check must not receive any approval heading.

Successful reviews use one exact first line, according to the actual assignment:

| Approval heading | Applicable work |
| --- | --- |
| `Self-review: LGTM` | Own or inherited implementation only under explicit user-approved self-review for this scope. |
| `Review: LGTM` | User-origin or implementing-worker-requested review in a different task, including bounded same-PR repairs with reviewer-as-contributor disclosure. |
| `Conflict resolution: LGTM` | Verified integration by the explicitly assigned `conflict-resolver` with review authority for the named PR set. |

These are the only approval headings; never use bare `OK`, bare `LGTM`, or another
variant. All require the same completed scope and verified evidence for the recorded
head/base; none claims independent human approval or guarantees that every behavior
was tested. Determine authorship from actual work, not the shared GitHub account.
A successor accepting the original implementation assignment finishes at `REVIEW_READY`,
including inherited work, and may self-review only with the user's explicit exception.
A separate requested reviewer making bounded repairs retains its review request and records
its contributor role; its corrections are not independently reviewed. Changing worker,
model or account alone does not make either case independent. Publish through the configured
OPS identity where required and retain actual worker, task, request or exception evidence.

Add the independent `MERGE_READY` label alongside `REVIEW_READY` only after a valid review,
current passing required checks and matching recorded/current head and base. Preserve the
review receipt and approval basis; an OPS author alone is not eligibility proof. If any
of those facts changes, remove `MERGE_READY` until the affected evidence is renewed.
New implementation returns to Draft/`OCCUPIED`; record and mirrors must agree. Keep earlier
reviews as history rather than rewriting their labels or claiming they cover new code.
Neither ready label nor any review heading grants merge, issue-edit or deployment rights.
An explicit resolver preserves original authors and follows the extra tree/sequence gates
in [conflict resolution](conflict-resolution.md); ordinary reviews do not activate them.

## Review rebase and publication

For an explicit user review request, complete this procedure within the named PR's isolated
owned worktree. An implementing-worker request alone does not invent history-rewrite authority;
use existing explicit or repository standing permission for that operation.

1. Fetch the target base and reviewed branch, record their full SHAs, inspect divergence and
   current write ownership, and preserve a recoverable pre-rebase checkpoint. Rebase onto the
   current target base before final MERGE_READY; if already current, no rewrite is needed.
   Preserve original commit authors, repair contribution and scope. Do not absorb foreign work.
2. Run affected verification and inspect the resulting review delta. Keep old/new head and base
   evidence in OPS; historical review receipts retain their original SHAs and meaning.
3. Prefer ordinary push. For the necessary rebase of the published reviewed branch, the explicit
   user review request authorizes only
   `--force-with-lease=refs/heads/<reviewed-branch>:<expected-remote-head-SHA>` to that exact branch.
   The expected full SHA is captured before rebasing and rechecked immediately before publication.
   A changed remote head, overlapping writer, failed lease or protection rejection blocks the
   push: reconcile, never refresh the lease blindly to overwrite new work. Plain force, unpinned
   leases, base-branch rewrites and protection bypass are forbidden. Verify the remote result.
4. Recheck the current remote head and target base immediately before readiness. Publish an
   eligible review and synchronize Ready/REVIEW_READY plus MERGE_READY only for that verified
   final head/base. If the base advances after readiness at a foreground checkpoint,
   invalidate MERGE_READY, return to Draft/OCCUPIED, then rebase/reverify the affected scope and
   renew the records. Reuse unchanged evidence; do not rewrite historical reviews. This is
   foreground continuation of the authorized task, not a background monitor or merge grant.

## Project-oriented reason codes

These are practical project categories, not an externally certified standard. Use a
code only when evidence supports it; do not require a finding in every category.

| Code | A blocking example |
| --- | --- |
| `CORRECTNESS` | A concrete input or state transition produces the wrong result. |
| `CONTRACT` | A caller, API/client schema, CLI, saved state or provider contract breaks. |
| `DATA_INTEGRITY` | Sources, citations, selected documents, usage records or rollback guarantees are lost or misrepresented. |
| `AUTHORIZATION` | Secrets, permissions, destructive scope or user-approved boundaries are violated. |
| `PERFORMANCE` | A measured regression blocks the relevant user flow or exceeds its required budget. |
| `VERIFICATION` | A required check fails, or necessary behavioral evidence is missing. |
| `INTEGRATION` | Conflicts, an incorrect base or foreign changes prevent the intended PR from landing safely. |

For data and provider changes, check identity preservation, selected inputs, budget
units, actual versus estimated usage, and safe schema behavior when relevant. Mock
checks do not establish live database behavior.

## Compact public outcomes

Use the guarded OPS renderer for requests, repair claims and results. Preserve the
schema's exact raw keys and types rather than inventing another human-only field set.
The result's first line is the eligible exact review heading; include implementation
provenance, review task, final head/base, contribution, evidence and outcome once. For
repairs, disclose that the reviewer contributed and its corrections are not independently
reviewed. Ordinary self-review records the user's explicit scoped authorization.

This request excerpt illustrates the canonical representation; resolve actual values
and validate the full configured request schema before publication:

```markdown
<!-- ops:review-request:v2:<review-id> -->
### Review requested

- scope: <implementation scope>
- worker: <implementing worker ID>
- assignment: <assignment ID>
- id: <review-id>
- head: <full head SHA>
- base: <full base SHA>
- task: <implementation task ID>
- issues: []
```

For unresolved blockers, use the configured change-request outcome with code, exact
issue/file/diff line, trigger, observed/expected behavior, evidence and required decision
or recheck. Omit an unassigned issue rather than inventing its number. Preserve the
reviewed head and do not copy an existing canonical record into a second JSON or prose
payload. Render `Verification blocked — VERIFICATION` for missing required evidence
instead of inventing a code defect. Historical review headings remain unchanged.

Use P1 for serious failures of a normal flow and P2 for bounded failures that still need
correction before the assigned scope is complete. Explain urgency with the impact;
priority alone is not a rejection reason. When verification alone is blocked, state
`Verification blocked — VERIFICATION` instead of inventing a code defect. Keep optional
suggestions clearly nonblocking and omit them when they add little value.
