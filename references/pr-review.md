# Requested PR review and bounded repair

Start from an explicit review request for the named PR and scope. Read current repository
rules, ownership, base/head, changes and existing evidence. Implementation completion
or REVIEW_READY alone does not request or authorize review.

## Review workflow

1. Establish the requested snapshot and actual reviewer/task. Preserve the original
   implementation identity and request provenance. Use the project's record tools;
   do not invent a parallel request schema or require redundant acknowledgement when
   a user-origin review already authorizes a ready, stopped scope.
2. Review changed behavior, its direct callers and relevant tests. Reproduce suspected
   defects. Reuse valid verification instead of rerunning every suite for each stage.
3. When the requested reviewer may repair clear implementation-scope defects, declare
   exact files/finding and obtain the project's temporary write ownership. Pause real
   overlapping writers, make the bounded correction, verify and commit/push with the
   configured development identity. Complex intent or added scope needs a decision.
4. Rebase onto the current target ref when the review grant includes it and it is needed.
   Preserve original changes/authors, use an isolated owned checkout, verify affected
   behavior and publish only under the approved expected-head lease. Never refresh a
   failed lease to overwrite another writer. A branch already current needs no rewrite.
5. Review the final relevant delta and publish the result for the matching head/base.
   Restore the project's ready state only after required evidence passes. An observed
   head/base/check change invalidates readiness until affected evidence is renewed.
   No background monitor or merge is implied.

A pure rebase is a preservation contribution, not a code correction. Disclose actual
reviewer-authored corrections once; do not describe them as independently reviewed.
Historical approvals keep their original snapshot and meaning.

## Results

| Heading | Eligibility |
| --- | --- |
| `Review: LGTM` | Requested review by a different worker/task, with any bounded corrections disclosed. |
| `Self-review: LGTM` | Original worker's review under an explicit scope-specific user exception. |
| `Conflict resolution: LGTM` | An explicitly assigned `conflict-resolver` with separate scoped authority. |

For a defect, give the exact location, trigger, observed versus expected behavior, fix
direction and focused verification. For success, state the outcome, reviewed snapshot,
relevant evidence and contribution/limitations concisely. Keep detailed records in the
project's canonical destination and preserve required machine-readable fields there.

Implementation checks alone must not publish an approval heading. GitHub bot identity
or a recorded worker ID does not establish independent human approval. Repository and
runtime authority still govern writes, messages, rebases and readiness.

For an explicitly authorized integration sequence, see
[conflict resolution](conflict-resolution.md); ordinary review does not grant merging.
