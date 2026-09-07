# Focused Pull Request Reviews

Ordinary worker reviews are off by default. The implementing worker must request a
review of its exact implementation scope, and a different conversation/task performs it.
A delivery checkpoint, ready label or repository tracking opt-in is not a request.
Do not review unrelated work, start a monitor or invent new implementation scope.

## Request and eligibility

- Preserve a durable request with implementing worker, Assignment, PR, implementation
  task identifier, requested scope, exact head/base and existing verification evidence.
  The reviewer records a different task identifier and its actual worker ID. A new model
  or ID in the same task is not a separate review. If task identity cannot be established,
  leave review pending instead of asserting separation. Missing chat history does not
  block ordinary user-approved succession; only review eligibility needs this evidence.
- The implementing worker may request review but may not waive separation or authorize
  its own self-review. Only explicit user approval for the named self-review permits that
  exception. Record the approval and mark the result as self-review, never independent
  or human approval. An implementation successor has the same restriction.
- A named commit-error or conflict resolver follows its explicit action/scope grant in
  [conflict resolution](conflict-resolution.md); a role name alone does not grant self-review.
- Use the configured guarded review request/publication operation where available. Check
  current owner, task separation or explicit exception, scope and head/base before writing.
  A request is not permission to create a new task if the runtime requires user authorization.

## Review and publication

1. Resolve the exact PR, base and head. Read the issue's acceptance checks when needed
   to interpret the diff. Inspect changed behavior, direct callers/contracts and test
   evidence; do not start a repository-wide audit by default.
2. Report reproducible correctness, contract, data, authorization or material performance
   problems. Style preferences, optional refactors and hypothetical risks are nonblocking.
3. Distinguish executed checks from checks reported by the PR author. Pending CI is
   pending verification, not proof of a product defect. Missing optional checks do not
   justify rejection; a required or risk-critical missing check can block approval.
4. Immediately before publishing, confirm the head still matches the reviewed commit.
   Review a changed delta before deciding. Pin the review to that commit. Reuse the prior
   result for unchanged heads rather than creating repetitive comments.
5. Use `APPROVE` or `REQUEST_CHANGES` only when publication and that review action are
   authorized and supported. If the signed-in account authored the PR, use `COMMENT`
   with the same clear outcome; never claim it created a formal approval or change request.
   A GitHub review can be submitted through `gh api .../pulls/<number>/reviews` using a
   JSON input file with `commit_id`, `event`, and `body`. Preserve actual newlines.

For corrections, identify the actual issue number, exact file and current diff line,
the concrete behavior to change, and the required recheck. Make the direction unambiguous.
Judge the implementation against the agreed outcome and code evidence, not against an
unpublished personal design. A further improvement is blocking only when necessary for
the authorized outcome; otherwise keep it explicitly optional.

Implementation ends with verified `REVIEW_READY` delivery and no approval heading.
For an eligible review, reuse the implementation and tester's passing evidence; inspect
the requested delta and rerun checks only for a relevant change or failure. An unfinished
scope, known blocker or pending required check must not receive any approval heading.

Successful reviews use one exact first line, according to the actual assignment:

| Approval heading | Applicable work |
| --- | --- |
| `Self-review: LGTM` | Own or inherited implementation only under explicit user-approved self-review for this scope. |
| `Review: LGTM` | Implementing-worker-requested review in a different task without implementation ownership. |
| `Conflict resolution: LGTM` | Verified integration by the explicitly assigned `conflict-resolver` with review authority for the named PR set. |

These are the only approval headings; never use bare `OK`, bare `LGTM`, or another
variant. All require the same completed scope and verified evidence for the recorded
head/base; none claims independent human approval or guarantees that every behavior
was tested. Determine authorship from actual work, not the shared GitHub account.
A successor accepting implementation ownership finishes at `REVIEW_READY`, including
inherited work. It may self-review only with the user's explicit exception. Changing
worker/model/account does not make the work independent. Publish through the configured
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

## Compact outcomes

Review of another worker's work:

```markdown
Review: LGTM

Reviewed `<head>` against `<base>`: <changed behavior and direct contracts checked>.
No blocking findings in this scope. Verification: <executed checks or clearly attributed PR evidence>.
```

Blocking finding (repeat only for independent defects):

```markdown
Changes requested — <CODE>

[P1/P2] #<actual issue> · <path:line> — <concrete problem>
- Trigger and result: <reproduction, observed behavior and expected behavior>.
- Evidence: <code/failed check>; <why this prevents the assigned outcome>.
- Required change and recheck: <observable correction and focused validation>.

Reviewed head: `<head>`.
```

Omit the issue field only when no issue is assigned; never invent a number.
Only for explicit user-approved self-review, use the same compact evidence format and
include the approval reference with this exact first line:

```markdown
Self-review: LGTM

Reviewed `<head>` against `<base>`: <own changed behavior and direct contracts checked>.
No blocking findings in this scope. Verification: <executed checks or reused tester evidence>.
```

Use P1 for serious failures of a normal flow and P2 for bounded failures that still need
correction before the assigned scope is complete. Explain urgency with the impact;
priority alone is not a rejection reason. When verification alone is blocked, state
`Verification blocked — VERIFICATION` instead of inventing a code defect. Keep optional
suggestions clearly nonblocking and omit them when they add little value.
