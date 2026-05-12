---
id: runnable-doc-examples
kind: skill
title: Runnable Doc Examples
description: >
  Public API examples that execute as tests. Go Example*, Rust doc fences,
  Python doctest, JS vitest. Output asserted. Docs drift; tested examples don't.
applies_when:
  - documenting a public API function
  - reviewing whether examples are up to date
  - examples exist as comments but are not tested
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

# Runnable Doc Examples

Doc examples that run as tests. Docs drift; tested examples don't.

## Mechanisms

| Stack          | Form                                          |
|----------------|-----------------------------------------------|
| Go             | `func Example*()` in `_test.go`; output comment asserted |
| Rust           | ` ```rust ` fences in `///` doc comments; `cargo test --doc` |
| Python         | `doctest` in docstrings; `pytest --doctest-modules` |
| JS / TS        | `vitest` or `jest` test tagged as doc example |

## Rules

- Every public API function has at least one runnable example.
- Example output is asserted, not just compiled.
- Example is the simplest real usage, not a stress test.
- Running `pytest --doctest-modules` (or stack equivalent) exercises them.

## Python Doctest Pattern

```python
def parse_age(raw: str) -> int | None:
    """Parse a non-negative integer age string.

    >>> parse_age("25")
    25
    >>> parse_age("abc")
    >>> parse_age("-1")
    """
```

## Keep Examples Minimal

One real use case per example. Not a tutorial. If the example is long, the API is
hard to use — that is signal to simplify the API, not expand the example.

## GOOD

Public `compress()` has a Python doctest. Running `pytest --doctest-modules` exercises
it. Change breaks example → example alerts you.

## BAD

```python
def compress(data: bytes, level: int) -> bytes:
    """Compress data.

    Example::
        # not runnable — not doctest format
        result = compress(b"hello", 3)
    """
```

Comment-style example, not a doctest. Docs drift after every refactor. Nobody knows.

## Red Flags

- Public API function with no runnable example.
- Example that compiles but asserts nothing about output.
- Example output comment that does not match actual output.
- `pytest --doctest-modules` (or stack equivalent) absent from CI.
