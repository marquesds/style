---
id: defensive-programming
kind: skill
title: Defensive Programming
description: >
  Harden edges: validate once, explicit contracts, fail-safe errors, bounded
  resources, concurrency hygiene. Use when hardening APIs, parsing untrusted
  input, concurrency, or "fail safe" / resilience reviews.
applies_when:
  - boundary validation and error strategy
  - untrusted or cross-service input
  - public APIs and concurrent workflows
  - resource limits and timeouts
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

# Defensive Programming

Assume accidents + hostility at **edges**. Core stays pure + honest via types + tests — skill:functional-core-imperative-shell. No FP conflict when defense lives at boundary; anti-pattern = nullable ladder **inside** core after parse.

## Boundaries

Parse / normalize / reject **once** at ingress. Inside: validated types only — skill:api-and-interface-design. No `dict` key guessing past boundary.

## Contracts

Pre/post/invariants explicit. Prefer types that ban illegal states — skill:liskov-and-design-by-contract.

## Errors

Separate **expected failure** (bad input, denied authz) from **bug** (broken invariant, `KeyError` in trusted core). No empty `except`; no `except Exception` masking normal outcomes.

Per **surface**, stick to one strategy: **value-style** (`Result` / tagged union) *or* **documented raises** at boundary — don't mix ad hoc. `raise` at edge OK when contract + outer handler map errors consistently (idiomatic Python). **Core**: no catch/retry for happy-path flow; use types that force handling when stack supports it.

Log state transitions; propagate correlation id (observability rule). Default deny / fail closed on authz — skill:owasp-top-ten.

## Resources

Cap size (payload, page limit). Timeouts on outbound I/O. Retry only safe ops — skill:resilience-retries. Prefer streaming when data unbounded (code-quality rule).

## Bounded access

Container access fails loudly when shape is unknown or empty.

- List index: `xs[0]` / `xs[-1]` only after `if xs:` guard or via `next(iter(xs), default)` / pattern match. Slice over index when shape unknown.
- Dict access: `.get(key, default)` at boundary; `d[k]` only on trusted typed contract — `KeyError` then signals a bug, not control flow.
- `pop` / `popitem` only on guaranteed-non-empty containers.
- Mutation while iterating: copy first or build new collection; never `del` from a list you are walking.
- Mutable default args (`def f(xs=[]):`) shared across calls — use `None` + factory.
- Numeric edges: divide-by-zero, overflow, NaN rejected at parse boundary, not deep in core.
- Resource cleanup: context managers always (`with open(...)`, `with uow:`); no naked `acquire` without a release path.

```python
def first_or(xs: list, default):
    return xs[0] if xs else default
```

## Concurrency + partial failure

One UoW / transaction per use case; don't leak half-written state — skill:unit-of-work-and-transactions. Watch stale reads / lost updates; use versioning or locks where contract demands.

## Security seams

Injection + path safety — skill:injection-defense. Secrets never logged or committed — skill:secrets-never-in-repo.

## Anti-patterns

Nullable ladder every line in trusted core. Swallow exceptions. Defaults that hide missing data. Re-validate same fields at every layer instead of one boundary. Blind index access on untrusted or empty container. Mutable default argument shared across calls. Naked resource acquire without context manager.

## Verification

Repro test before fix; regression guards — skill:bug-first-debugging. Property tests for invariants types can't encode.

## GOOD

Boundary **A**: `raise` when callers/handlers know the contract and translate to HTTP or domain errors.

```python
def parse_age(raw: str) -> int:
    n = int(raw)
    if n < 0 or n > 150:
        raise ValueError("age out of range")
    return n
```

Boundary **B**: value-style expected failure — caller **must** branch; no lying sentinel int.

```python
def parse_age(raw: str) -> int | None:
    try:
        n = int(raw)
    except ValueError:
        return None
    if n < 0 or n > 150:
        return None
    return n
```

## BAD

```python
def parse_age(raw: str) -> int:
    try:
        n = int(raw)
    except Exception:
        return 0
    return n if n > 0 else 0
```

Problem = blanket except + fake default — not “exceptions forbidden elsewhere.”

## Red Flags

- `xs[0]` with no guard; crashes on empty input at runtime, not parse time.
- `d["key"]` on an externally sourced dict — `KeyError` swallowed or unhandled.
- `def fn(items=[]):` — shared mutable default, state bleeds across calls.
- `except Exception: pass` or `except Exception: return default` — hides real bugs.
- Resource opened without `with`; cleanup skipped on exception path.
- Divide-by-zero or NaN only discovered deep in a calculation, not at the boundary.
- Validation duplicated at every layer instead of once at ingress.
