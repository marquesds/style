---
id: code-quality
kind: rule
title: Code Quality
description: >
  Max 200 lines per file. Max 10 lines per function. Low cyclomatic complexity.
  Iterator chains over loops. Demand elegance on nontrivial change.
applies_when:
  - any source change
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

# Code Quality

Small files. Small functions. Flat logic. No surprises.

## Hard Limits

| Limit | Value |
|---|---|
| File length | 200 lines (incl. `.md`) |
| Function length | 10 lines body |
| Cyclomatic complexity | low; prefer match + iterator chain |

Hit a limit → split. Don't bypass.

## Demand Elegance

Nontrivial change: pause. Ask: more elegant way?
Hacky fix landed: schedule rewrite. "Knowing now what we know, redo cleanly."

Skip for obvious one-liners. Challenge own work before presenting.

## Functional Bias

Iterator chains, comprehensions, pattern matching > nested conditionals + mutation. Logic flat. Data flow obvious.

## Streaming / Bounded Memory

Data can grow → default **lazy**: generators, iterator pipelines, chunked I/O, DB/server-side **cursor** iteration. Materialize `list` / `set` only when size bound proven or API demands concrete collection.

## GOOD

```python
def summarize(events: list[Event]) -> list[Summary]:
    return [summarize_one(e) for e in events if e.is_valid()]

def discount(order: Order) -> Price:
    match order.tier:
        case Tier.VIP: return Price.ZERO
        case Tier.STANDARD: return order.price
```

```python
def active_ids(conn):
    cur = conn.execute("SELECT id FROM users WHERE active")
    for row in cur:
        yield row[0]
```

Small, single-purpose, no mutation. Reads like spec. Stream path: one row at a time, no giant `list(all_rows)`.

## BAD

```python
def summarize(events):
    results = []
    for e in events:
        if e.is_valid():
            s = summarize_one(e)
            results.append(s)
    return results

def discount(order):
    if order.tier == "VIP":
        if order.price > 100:
            ...
        else:
            ...
    else:
        if order.seasonal_promo:
            ...
        else:
            ...
```

```python
def load_everything(conn):
    rows = list(conn.execute("SELECT * FROM huge").fetchall())
    return [r for r in rows if r["ok"]]
```

Untyped. Mutable accumulator. Deep nesting. Branching too wide. Full fetch + filter in memory when cursor + predicate stream would do.

## Red Flags

- File creeping past 200 lines.
- Function past 10 lines body.
- Three+ levels of nesting.
- Boolean parameters that select different behaviors.
- Mutation inside a function returning a value.
