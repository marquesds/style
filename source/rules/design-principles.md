---
id: design-principles
kind: rule
title: Design Principles
description: >
  Functional core / imperative shell. Pure functions. Postpone side effects.
  Sinks not pipes. SOLID with LSP first (precondition + invariant + postcondition).
applies_when:
  - any new module
  - any architectural decision
always_apply: true
globs: "**/*"
agents:
  claude: { kind: rule }
  cursor: { kind: rule, glob: "**/*" }
  codex:  { section: rules }
  openclaw: { section: rules }
  opencode: { kind: rule }
  pi:       { section: rules }
  vibe:   { kind: rule }
---

# Design Principles

Pure core. Effects at the edge. Honest interfaces. LSP holds always.

## Functional Core / Imperative Shell

Pure functions hold logic. Side effects live at the boundary. Immutability default. Referential transparency. Effects postponed to last stage.

See skill:functional-core-imperative-shell.

## Postpone Side Effects

Compute first. Persist last. Validate, transform, decide → then write to DB / network / disk.

## Sinks, Not Pipes

Component receives input, does work, returns. No cascading hidden effects. Blast radius bounded.

```text
GOOD: send_welcome_email(user) → mailer.deliver(...)
BAD:  create_user(attrs) → DB write + email + analytics + audit + ...
```

## SOLID — LSP First

Subtypes substitute base types without breaking callers.
Contract = precondition + invariant + postcondition.

- Subtype precondition: equal or weaker.
- Subtype postcondition: equal or stronger.
- Invariants preserved.

Violate any → refactor. Don't paper over with `isinstance` checks.

See skill:liskov-and-design-by-contract.

## Deep Modules, Honest Interfaces

Public surface tells truth about what module does. Internals hidden. Callers reason without reading source.

## Core Habits

- **Simplicity first**: minimal change footprint.
- **No laziness**: root cause, no workarounds.
- **Minimal blast radius**: touch only necessary.

## GOOD

```python
def total(items: list[Item]) -> Money:
    return sum((i.price for i in items), Money.zero())

async def checkout(state: State, db: Db) -> Receipt:
    receipt = build_receipt(state, total(state.items))
    await db.save(receipt)
    return receipt
```

Pure `total` and `build_receipt`. I/O at the shell.

## BAD

```python
async def total(items, db):
    s = Money.zero()
    for i in items:
        p = await db.get_product(i.id)
        s += p.price
    return s
```

DB call inside logic. Untestable without mocks. Effects mixed with computation.

## Red Flags

- I/O call in a function named like pure logic (`compute_*`, `calculate_*`).
- Subclass that throws `NotImplementedError` for a base method.
- Module's public function does five unrelated things.
- One write triggers four invisible follow-on writes.
