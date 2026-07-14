---
id: code-quality
kind: rule
title: Code Quality
description: "Production implementation modules: max 200 lines per file and 10 lines per function. Keep complexity low; prefer iterator chains over loops. Docs, skills, specs, and tests are exempt from the file cap."
applies_when:
  - any source change
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

# Code Quality

Keep files small, functions short, and logic flat. Avoid surprises.

## Hard Limits

| Limit | Value |
|---|---|
| Production implementation module length | 200 lines |
| Function length | 10 lines body |
| Cyclomatic complexity | low; prefer match + iterator chain |

If production implementation code hits a limit, split it instead of bypassing the rule.

Documentation, skills, specifications, tests, fixtures, generated files, and data declarations
are exempt from the **file-length** cap. Keep those files readable, but do not split cohesive
content merely to reach an arbitrary line count.

## Demand Elegance

For a nontrivial change, pause and ask whether there is a simpler shape.
Hacky fix landed: schedule rewrite. "Knowing now what we know, redo cleanly."

Skip this for obvious one-liners. Challenge your own work before presenting it.

## Functional Bias

Prefer iterator chains, comprehensions, and pattern matching over nested conditionals and mutation. Keep data flow obvious.

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

## Carve-outs

Caps apply to **logic**. Some shapes are exempt by structure, not author whim:

- **Large `@dataclass` / `TypedDict`** with many named fields — data bags are not
  logic; line count comes from field declarations, not complexity.
- **Generated code** (schemas, parsers, serializers) — machine-produced; don't
  hand-edit to fit the limit; regenerate from source instead.
- **Exhaustive enum-like dicts** (`STATUS_LABELS`, `COUNTRY_CODES`) — length is
  the point; split would destroy locality.
- **State-machine transition tables** — all transitions in one place is a feature;
  scatter across files to hit the cap and you lose the whole picture.

If unsure whether a file qualifies: ask "does complexity grow with size here?"
If yes, split. If no (it's a data declaration), the carve-out applies.

## Red Flags

- Production implementation module creeping past 200 lines.
- Function past 10 lines body.
- Three+ levels of nesting.
- Boolean parameters that select different behaviors.
- Mutation inside a function returning a value.
