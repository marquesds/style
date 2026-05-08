---
id: code-review-and-quality
kind: skill
title: Code Review (Five-Axis)
description: >
  Multi-axis review before merge: correctness, readability, architecture,
  security, performance. Severity labels keep signal clear.
applies_when:
  - reviewing a PR
  - self-review before push
  - reviewing AI-generated code
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  vibe:   { kind: skill }
---

# Code Review (Five-Axis)

Five axes, every change. No "looks good" without checks.

## Axes

### 1. Correctness

- Matches spec / task?
- Edge cases handled (None, empty, boundary, overflow)?
- Error paths covered, not just happy?
- Tests actually pin behavior (not implementation)?

### 2. Readability

- Names match project conventions?
- Control flow flat?
- Could it be shorter / clearer?
- Abstractions earn their cost?

### 3. Architecture

- Module boundaries respected?
- Dependencies flow inward (see skill:hexagonal-architecture)?
- Public API change minimal and additive?
- LSP holds (see skill:liskov-and-design-by-contract)?

### 4. Security

- Input validated at boundaries?
- No secrets in code, logs, or fixtures?
- Auth checked at every entry point?
- No SQL string concat, no `eval`, no shell-out with user input?

### 5. Performance

- N+1 queries (see skill:n-plus-one-prevention)?
- Unbounded allocations or loops?
- Blocking call in async path?
- Cloning hot data unnecessarily?

## Severity Labels

| Prefix | Meaning |
|---|---|
| (none) | Required before merge |
| **Critical:** | Blocks merge — security, data loss, broken behavior |
| **Optional:** | Worth considering, author may decline |
| **Nit:** | Minor — author may ignore |
| **FYI:** | Info only |

## Change Sizing

```text
~100 lines  good (one sitting)
~300 lines  ok if one logical change
~1000 lines split it
```

## GOOD

```text
- src/checkout.py:42: Critical: SQL string concatenation; use parameter binding.
- src/cart.py:88: total() recomputes on every render; memoize on cart.id.
- src/cart.py:120: Optional: extract `taxable_subtotal` for clarity.
- tests/test_cart.py: Nit: trailing whitespace.
```

Specific. Actionable. Severity labeled.

## BAD

```text
LGTM!
```

No evidence of any axis being checked.

## Process

1. Read the spec / ticket.
2. Read the tests first — they tell intent.
3. Walk implementation against five axes.
4. Label findings.
5. Verify suite + lint + types pass locally.

## Red Flags

- PR merged without any review comments.
- Reviewer's only feedback is style nits.
- Bug fix without a regression test.
- Large PR ("too big to review") merged anyway.
- Same reviewer always rubber-stamps the same author.
