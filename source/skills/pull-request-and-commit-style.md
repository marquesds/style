---
id: pull-request-and-commit-style
kind: skill
title: PR + Commit Style
description: >
  Conventional Commits. ~100-line PRs. One logical change per PR. Feature flags
  when applicable. Commit body and PR description lead with the cause — who
  hurts or what gain is lost without this change — before the approach.
applies_when:
  - opening a PR
  - writing commit messages
  - splitting work into reviewable units
agents:
  claude: { kind: skill }
  cursor: { kind: skill }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# PR + Commit Style

Small. Atomic. Reversible. Reviewer thanks you. Reviewer reads the **why**
first — the cause this change exists in the world — and only then the
mechanism. A PR or commit whose purpose is invisible costs the reviewer time
they cannot bill back.

## Conventional Commits

```text
<type>(<scope>): <subject>

<body: lead with the cause — who or what hurts (or what gain is lost)
without this change. Add a second paragraph on approach only when the
shape needs defense (trade-off, constraint, non-obvious choice).>

<footer: refs, breaking changes>
```

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `revert`.

Subject: imperative mood, ≤ 50 chars, no trailing period.

```text
feat(sessions): add idempotent reset endpoint

Support kept hitting INC-4221: duplicated reset calls corrupted the audit log
and forced manual cleanup. New endpoint dedupes via Idempotency-Key so retries
are safe.

Reset preserves audit trail via outbox in the same UoW. Closes INC-4221.
```

First paragraph = cause (support pain, broken audit log). Second = approach
(outbox, same UoW). Reviewer scans the cause and already knows whether the
change is worth their time.

## PR Sizing

| Lines | Verdict |
|---|---|
| ~100 | ideal |
| ~300 | ok if one logical change |
| ~1000 | split |

One logical change per PR. Refactor + feature in one PR → split.

## PR Template

```markdown
## Why
What breaks for whom — or what gain is lost — if this doesn't merge.
One sentence. Name a victim or a metric, not "improve X".

## What
The change in user-visible terms. Link spec / ticket / incident.

## How
Approach taken. Trade-offs considered. Alternatives rejected.

## Test plan
- [ ] unit
- [ ] integration
- [ ] manual repro for the original bug
- [ ] perf budget verified (no new N+1)
- [ ] observability hooks added

## Risk + rollback
Behind a flag? Migration step? How to undo?
```

`Why` comes first deliberately. A reviewer who can't tell *why this PR exists*
after reading the first section will not give a useful review of *how* it was
built. If `Why` is blank, vague, or paraphrases the PR title, send it back to
the author before reading the diff.

If the work used `blind mode`, include the `Blind Mode Disclosure` block from
skill:requirements-crushing in the PR description.

## Feature Flags When Applicable

Risky / cross-team / partial change → ship behind a flag. Default off. Rollout in stages. Flag has a removal date.

## GOOD

```text
fix(billing): zero-amount transfer no longer creates outbox row

Downstream consumers were paging on TransferCompleted events with amount=0,
masking real signals during the Black Friday weekend.

Adds invariant in the domain to drop empty transfers before the outbox write,
plus a regression test pinned to INC-9921. Closes INC-9921.
```

Cause-first paragraph names the victim (on-call, downstream consumers) and
the gain (no false pages). Approach paragraph defends the shape (domain
invariant + regression test). Bug ID stays in the footer.

```markdown
## Why
Free-tier users currently see the export button but every click 403s,
generating ~30 support tickets/week tagged "can't export".

## What
Hide the export button for free-tier accounts. Endpoint already 403s; this PR
only touches the UI.

## How
Read the existing entitlement flag in the layout shell. Considered a
server-rendered partial swap and rejected it — entitlement is already in
the client store.
```

`Why` names a victim (free users, support) and a metric (tickets/week).
Reviewer knows in one sentence whether the work is worth merging.

## BAD

```text
stuff
```

```text
fixed bug; also refactored some unrelated stuff in cart.py and bumped lodash
```

```text
fix(api): handle null

Refactor the handler to return early on null input.
```

Body explains code, not cause. Reviewer learns *what the diff does* (already
visible in the diff) and *nothing about why it needed to exist*.

```markdown
## Why
Improve the export experience.

## What
Hides the export button for free users.
```

Why paraphrases the PR title with a verb. No victim, no metric. Bounce.

## Pre-PR Checklist

- [ ] Tests green locally.
- [ ] Lint + types clean.
- [ ] Self-review against five axes (skill:code-review-and-quality).
- [ ] Definition of Done walked (skill:definition-of-done).
- [ ] Commit messages tell the story; no `wip` / `fix typo` mixed in.
- [ ] Blind-mode work discloses unanswered questions and assumed answers.

## Red Flags

- Commit body explains the code, not the cause — restates the diff in prose.
- Commit body opens with "This change…" or "Refactors X to do Y" before saying
  why the change was needed.
- PR `## Why` is blank, paraphrases the title, or reads "improve / better /
  cleaner" with no named victim or metric.
- PR description: "see commits".
- Blind-mode PR missing the `Blind Mode Disclosure` block.
- Reviewer can't say what breaks if the PR doesn't merge after reading the
  first section.
- 30 commits, 12 of them `wip`.
- Unrelated formatting changes in a feature PR.
- "Will address in a follow-up" — usually means never.
