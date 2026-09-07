# Focused Pull Request Reviews

Use this mode for an explicitly requested review or a repository-authorized review
checkpoint. Where the repository requests peer review at delivery, preserve the
assigned implementation queue and review only the relevant delta. Do not create a monitor.

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

For this worker's completed PR, reuse the implementation and tester's passing evidence.
Briefly inspect the final diff and immediately post `Self-review: LGTM` if it has no
blocker; do not add a second audit or rerun valid tests. Recheck only a relevant new
change or failure and name the reviewed head. An unfinished scope, known blocker or
pending required check must not receive either approval label.

Successful reviews use exactly `Self-review: LGTM` as the first line for the reviewer's
own work or `Review: LGTM` for another worker's work. These are the only approval labels;
never use bare `OK`, bare `LGTM`, or another variant. Determine ownership from actual
work, not the shared GitHub account. Neither label is independent human approval or a
guarantee that every behavior was tested. A review never grants permission to merge or deploy.

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
For a self-review completion, use the same compact evidence format with this exact first line:

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
