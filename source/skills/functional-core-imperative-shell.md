---
id: functional-core-imperative-shell
kind: skill
title: Functional Core / Imperative Shell
description: >
  Pure logic in the core. I/O at the boundary. Effects postponed to last stage.
  Tests run fast and deterministic.
applies_when:
  - any new module with logic and I/O
  - mixing computation with side effects
  - tests slow because of mocks
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

# Functional Core / Imperative Shell

Pure decides. Shell acts. Effects last.

## The Shape

```text
input → [pure compute] → decisions → [imperative apply] → output
        ^ no I/O here ^                ^ DB / HTTP here ^
```

Pure core: deterministic functions over plain data. Same input → same output. No global state. No clocks. No DB. Pass time and randomness in.

Shell: thin. Reads inputs from the world, calls core, writes results back.

## Postpone Side Effects

Compute, validate, plan → THEN persist. Effects at the very last stage. Easy to inspect, easy to revert, easy to trace.

## Pure Functions

| Property | Why |
|---|---|
| Deterministic | Same input → same output |
| No mutation | Old values still valid for callers |
| No I/O | Tests run microseconds |
| Total or explicit failure | `Result` / `Either` over exceptions for expected errors |

## Inject Effects

Time, randomness, DB, HTTP — pass as dependencies. Don't fetch them yourself.

## GOOD

```python
@dataclass(frozen=True)
class CartTotal:
    subtotal: Money
    discount: Money
    total: Money

def total(cart: Cart, now: datetime) -> CartTotal:
    sub = sum((i.price for i in cart.items), Money.zero())
    disc = seasonal_discount(cart, now)
    return CartTotal(sub, disc, sub - disc)

async def checkout(cart: Cart, db: Db, clock: Clock) -> Receipt:
    breakdown = total(cart, clock.now())
    receipt = build_receipt(cart, breakdown)
    await db.save(receipt)
    return receipt
```

Pure `total` + `build_receipt`. Shell `checkout` does I/O once at the end.

## BAD

```python
async def total(cart, db):
    s = Money.zero()
    for i in cart.items:
        p = await db.get_product(i.id)
        s += p.price
    return s
```

DB call inside compute. Untestable without mocking DB. Effects scattered.

## Refactor Recipe

1. Identify side effects in a function.
2. Extract pure computation as a new function over plain data.
3. Pass needed inputs explicitly.
4. Move I/O to the caller.
5. Tests for the pure function need zero mocks.

## Red Flags

- `await`, `requests.get`, `db.execute` inside a function named `compute_*`, `calculate_*`, `build_*`.
- Pure-looking function reads `datetime.utcnow()`, `time.time()`, `os.environ`, `random.*`.
- Tests filled with mock setup that mirrors real wiring.
- Effects fan out before the decision is made (write five times for one decision).
