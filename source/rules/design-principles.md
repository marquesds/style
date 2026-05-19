---
id: design-principles
kind: rule
title: Design Principles
description: >
  Functional core / imperative shell. Favor referentially transparent
  functions for logic. Parnas information hiding; weaker connascence; GRASP.
  SOLID with LSP first. High cohesion, low coupling. Law of Demeter. YAGNI.
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

Keep the core pure, put effects at the edge, design honest interfaces, and preserve LSP.

## Functional Core / Imperative Shell

Pure functions hold logic. Side effects live at the boundary. Immutability default. Effects postponed to last stage.

See skill:functional-core-imperative-shell.

## Referential Transparency

**Favor** functions where **same inputs ⇒ same output** and **no hidden** observable effect: no sneaky I/O, globals, env reads, `now()`, RNG, or **in-place mutation** of arguments. Caller can substitute `f(x)` with its value. Time, randomness, clocks → **explicit parameters** or **shell** only (inject ports, don’t reach inside “pure” logic).

## Postpone Side Effects

Compute first and persist last. Validate, transform, and decide before writing to the DB, network, or disk.

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

## Information Hiding (Parnas), Deep Modules, Honest Interfaces

**Parnas:** hide **design decisions likely to change**. Stable boundary; callers depend on **semantics**, not storage or ordering inside. Public surface **honest** about **what** module does; **how** stays private — deep module, no spelunking.

## AI-Ready Architecture

Module boundaries discoverable without reading internals. Public interface tells truth about what module does.

- Name + type signatures + a catalog entry are the contract. Agent reads imports and signatures to plan; opaque or misleading surfaces force deep crawl, eat context, and drive wrong patches.
- A module named `process_*` that secretly writes to a DB violates honest interfaces — it will be called in the wrong place by any reader, human or AI.
- This is the Parnas / honest-interfaces principle restated for agent collaboration: strong names, typed signatures, and manifest-visible ports let agents plan changes without spelunking internals.
- Surface design: skill:api-and-interface-design. Slice-by-feature discoverability: skill:hexagonal-architecture.

## Connascence

Parts share a **secret agreement** = connascence. Prefer **weaker** forms (easier to change). Rough strength: Name < Type < Meaning < Position (broadly, static < dynamic). Two files both interpret the same bare `dict` key strings and churn together → name/type the contract. Caller uses `row[0]` / tuple slots ↔ **connascence of position**; give a **named** operation (`best_bid()`, not `(price, qty, ts)[0]`). Refactor until the shared secret shrinks.

## GRASP (Larman)

Craig Larman — responsibility assignment: **Information Expert**, **Creator**, **Controller**; **Low Coupling** + **High Cohesion** (below); **Polymorphism** (kill type switches); **Pure Fabrication** (invented class to keep cohesion); **Indirection** (mediate); **Protected Variations** (port around predicted change ↔ hex).

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
- **Referential transparency** for logic: pure data in, data out — effects named and at edge.

## GOOD

```python
def total(items: list[Item]) -> Money:
    return sum((i.price for i in items), Money.zero())

async def checkout(state: State, db: Db) -> Receipt:
    receipt = build_receipt(state, total(state.items))
    await db.save(receipt)
    return receipt
```

Pure `total` and `build_receipt`. I/O at shell. Module hides **pricing rules**; `checkout` doesn’t read SKU tables directly.

```python
class OrderBook:
    def best_bid(self) -> Price | None: ...

def quote(book: OrderBook) -> str:
    p = book.best_bid()
    return "n/a" if p is None else str(p)
```

Heap vs sorted list stays inside `OrderBook` — **information hiding**.

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

```python
def notional(row: tuple[int, str, float]) -> float:
    return row[0] * row[2]  # tuple shape is the secret API — connascence of position

def area(shape: object) -> float:
    if isinstance(shape, Circle):
        return pi * shape.r**2
    if isinstance(shape, Rect):
        return shape.w * shape.h
    return 0.0
```

Position + scattered `isinstance` ladder — use **named types** / **polymorphism** (GRASP **Protected Variations**).

```python
def line_total(qty: int, unit: Money) -> Money:
    metrics.increment("line_total")  # hidden effect — not replaceable by value
    return unit * qty
```

Looks like math; **observably** not referentially transparent.

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
- Callers coupled to **field order** / **tuple layout** of another module’s data.
- **Type switches** scattered instead of polymorphism or a single port.
- `compute_*` / `pure`-shaped fn touches **clock**, **env**, **singleton**, **metrics**, or **mutates** args.
