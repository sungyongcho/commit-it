# Changelog

## Unreleased

- End ordinary worker delivery at REVIEW_READY; require an implementing-worker review
  request and a different task, with ordinary self-review only by explicit user approval.
- Add MERGE_READY alongside REVIEW_READY after eligible review and current head/base/checks;
  invalidate it when the underlying evidence changes without granting merge authority.
- Permit named commit-error/conflict resolvers to close assigned PRs, edit assigned issues
  and self-review only under explicit scoped grants; retain original authors and history.

## 3.0.0 - 2026-09-07

- Replace predecessor-acknowledged ownership transfer with explicit user-approved succession,
  preserved checkpoints and project assignment lineage independent of disposable chats.
- Allocate collision-checked worker IDs while retaining existing IDs and v1 work-state records;
  record successor/model verification without implying independent review or merge authority.
- Define OPS-attributed ownership, commit/PR receipts and synchronized managed labels while
  retaining personal development authorship and existing repository permissions.
- Name conversations through available official client tools, with verified results and
  a capability-based fallback that never edits internal conversation storage.
- This major version changes the coordination and handoff contract. Existing records remain
  readable; label provisioning, tags, releases and account activation are not implicit.

## 2.9.0 - 2026-09-07

- Add explicitly assigned conflict resolution, a durable merge sequence, exact review
  headings and verified foreground squash/resume receipts while preserving worker authority.
- Share one editable local source across Codex, Claude Code and Gemini discovery paths.
- Add a fixed eleven-file release inventory, explicit managed-copy updates and retained
  backups; refuse unknown drift, redirected parents and replacement of Git authoring roots.
- Document current-source rereads, per-agent installation, guarded source maintenance
  and release-time version selection.
