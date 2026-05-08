---
id: design-principles
kind: rule
title: Design Principles
description: >
  Functional core / imperative shell. Pure functions. Postpone side effects.
  Sinks not pipes. SOLID with LSP first (precondition + invariant + postcondition).
  High cohesion, low coupling at module/API boundaries. Law of Demeter (least
  knowledge). YAGNI.
applies_when:
  - any new module
  - any architectural decision
always_apply: true
globs: "**/*"
agents:
  claude: { kind: rule }
  cursor: { kind: rule, glob: "**/*" }
  codex:  { section: rules }
  goose:  { section: rules }
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

## High Cohesion, Low Coupling

**Cohesion:** what changes together lives together. One clear reason to change per unit.

**Coupling:** pay only for dependencies that earn their keep. Hide incidental detail behind boundaries (FCIS + honest interfaces).

**Afferent** (incoming): others reference you — high fan-in amplifies blast radius when internals or contract slip. **Efferent** (outgoing): you depend on others — high fan-out inherits their churn. Prefer volatile pieces **high efferent, low afferent** so fewer dependents shake when you refactor. Stable, widely referenced surfaces accrete afferent coupling — treat them as real contracts.

**Law of Demeter (least knowledge):** a unit talks only to **immediate collaborators** — no “friend of a friend” via long chains (`a.b().c().d()` train wrecks). Put traversal and disclosure behind the **owner** (method on aggregate, façade, port), not callers reaching through foreign internals. Reinforces low coupling and deep modules.

```text
GOOD: order.buyer_contact() → one collaborator
BAD:  order.buyer().account().person().email() → chain owns your graph
```

[Deeper: afferente vs eferente](https://elemarjr.com/livros/arquiteturadesoftware/volume-1/entendendo-e-convivendo-com-o-acoplamento/#Acoplamento_aferente_e_eferente). Test strategy for high fan-in: skill:test-design. Package by feature (hex inside each slice): skill:hexagonal-architecture.

## YAGNI

**You Aren’t Gonna Need It:** implement **today’s** requirement — no speculative abstraction, configuration toggles, plugin tiers, or extra layers until **two concrete callers**, recurring churn, or a **measurable constraint** pulls them in. Prefer the smallest shape **until duplication hurts**. Fewer hypothetical futures ⇒ less coupling and less head load.

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
- Unrelated responsibilities glued in one module (low cohesion).
- Hub referenced by many, guarded only by shallow or interaction-only tests.
- One feature forces coordinated edits across distant, unrelated packages.
- Train-wreck chains or getters exposed only so outsiders can keep navigating across boundaries.
- Unused knobs, strategy branches, or interfaces maintained “for flexibility” nobody uses.
- Alternate code paths exercised only by tests or mocks for hypothetical callers.
