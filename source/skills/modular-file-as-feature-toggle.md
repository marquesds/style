---
id: modular-file-as-feature-toggle
kind: skill
title: Modular File as Feature Toggle
description: "Split source by capability axis. Optional capability = removable file. Document the toggle at the top of each optional file. Complements compile-time feature flags when the capability boundary is clean enough that a file is the feature."
applies_when:
  - designing a library with optional or variant capabilities
  - separating mutable from immutable variants
  - creating a minimal core with opt-in extras
  - reviewing whether a file has one clear responsibility
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

# Modular File as Feature Toggle

Split capabilities into files. An optional capability should be a removable file.

## Shape

Source files map to capability axes:

```text
core.py        — always required; no optional deps
operators.py   — derived operations built on core
relations.py   — comparison and membership
updaters.py    — mutation methods (omit for an immutable variant)
```

Removing `updaters.py` produces an immutable variant without a rewrite.

## Document the Toggle at the Top

Each optional file states what the system loses if it is removed:

```python
# updaters.py
# Optional capability: mutation methods (Add, Remove, Clear) for Set.
# Omit this file for an immutable-only build; all other modules stay intact.
```

Reader immediately knows: this file is optional, and here is what removing it costs.

## Rules

- Each optional file is self-contained: no `from .updaters import` in `core.py`.
- Core imports only from `core.py` and stdlib. Optional files import from core.
- Tests per file cover that file's capability. Removing the file removes its tests cleanly.
- Optional files must not mutate or inject global state at import time.

## Complements Compile-Time Feature Flags

Source-level toggle (delete a file) is a stronger variant of a compile-time flag
(skill:compile-time-feature-flags). Use source-level when the capability boundary is
clean enough that the file is the feature, with no guarded `#[cfg]` scaffolding needed.

## When to Use

- Variant products from one codebase (paid vs free, mutable vs immutable).
- A dependency-heavy capability that should be truly optional.
- Tutorials or embedded contexts where the smallest surface matters.

## GOOD

```text
lib/
  core.go       # Set[T] core — always shipped
  operators.go  # Union, Intersection, Difference — optional
  relations.go  # Subset, Superset — optional
  updaters.go   # Add, Remove, Clear — omit for immutable variant
```

README: "Delete `updaters.go` for an immutable `Set`."

## BAD

Optional capability implemented as a boolean parameter:

```python
def make_set(items, mutable=True) -> Set:
    ...
```

Boolean parameter selects behavior at runtime. Both code paths always compiled in.
Callers must know the flag exists. Hard to remove later (skill:deprecation-and-migration).

## Red Flags

- Core module imports from an optional module at the top level.
- Removing an "optional" file breaks unrelated tests.
- Toggle not documented in the optional file's header.
- All capabilities in one file; the file has no single reason to change.
