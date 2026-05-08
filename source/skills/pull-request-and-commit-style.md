---
id: pull-request-and-commit-style
kind: skill
title: PR + Commit Style
description: >
  Conventional Commits. ~100-line PRs. One logical change per PR.
  Feature flags when applicable. PR template: context, why, test plan.
applies_when:
  - opening a PR
  - writing commit messages
  - splitting work into reviewable units
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# PR + Commit Style

Small. Atomic. Reversible. Reviewer thanks you.

## Conventional Commits

```text
<type>(<scope>): <subject>

<body explaining why, not what>

<footer: refs, breaking changes>
```

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `revert`.

Subject: imperative mood, ≤ 50 chars, no trailing period.

```text
feat(sessions): add idempotent reset endpoint

Reset preserves audit trail via outbox; same UoW. Closes INC-4221.
Adds /v1/sessions/{id}/reset with Idempotency-Key header.
```

## PR Sizing

| Lines | Verdict |
|---|---|
| ~100 | ideal |
| ~300 | ok if one logical change |
| ~1000 | split |

One logical change per PR. Refactor + feature in one PR → split.

## PR Template

```markdown
## Context
What problem is this solving? Link spec / ticket / incident.

## Why this approach
Trade-offs considered. Alternatives rejected.

## Test plan
- [ ] unit
- [ ] integration
- [ ] manual repro for the original bug
- [ ] perf budget verified (no new N+1)
- [ ] observability hooks added

## Risk + rollback
Behind a flag? Migration step? How to undo?
```

## Feature Flags When Applicable

Risky / cross-team / partial change → ship behind a flag. Default off. Rollout in stages. Flag has a removal date.

## GOOD

```text
fix(billing): zero-amount transfer no longer creates outbox row

Empty transfer was generating a TransferCompleted event with amount=0,
spamming downstream. Adds invariant in domain + regression test.

Closes INC-9921.
```

Short subject. Why included. Bug ID in footer, not in test name.

## BAD

```text
stuff
```

```text
fixed bug; also refactored some unrelated stuff in cart.py and bumped lodash
```

Multi-purpose, unreviewable, history loses signal.

## Pre-PR Checklist

- [ ] Tests green locally.
- [ ] Lint + types clean.
- [ ] Self-review against five axes (skill:code-review-and-quality).
- [ ] Definition of Done walked (skill:definition-of-done).
- [ ] Commit messages tell the story; no `wip` / `fix typo` mixed in.

## Red Flags

- Commit message that re-states the diff line by line.
- PR description: "see commits".
- 30 commits, 12 of them `wip`.
- Unrelated formatting changes in a feature PR.
- "Will address in a follow-up" — usually means never.
