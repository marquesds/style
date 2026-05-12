---
id: bindings-as-thin-wrappers
kind: skill
title: Bindings as Thin Wrappers
description: >
  Core library once. Per-platform bindings (Python, JS/WASM, Go, C-ABI) translate
  types only. No logic reimplemented in bindings. One source of truth.
applies_when:
  - exposing a library to multiple languages or runtimes
  - adding a new language binding to an existing core
  - reviewing a binding PR for leaked logic
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

# Bindings as Thin Wrappers

Core library once. Bindings translate types. No logic in bindings.

## Shape

```text
core-lib  (Rust / C / Go)
    ↓           ↓           ↓
py-binding  js-binding  go-binding
  type map only — no business rules
```

Bindings: marshal types, expose the core API surface, map errors. Nothing else.

## Why

Business logic in bindings = duplicated logic. A fix in the core requires matching
fixes in Python, JS, and Go. Drift is inevitable when the same rule lives in three
places.

## Rules

- Binding function calls one core function, maps its return type, maps its error. That is all.
- Binding holds no state.
- Binding does no validation the core does not already do.
- Error types mapped once per binding (not per function).

## Type Map Pattern

```rust
// core
pub fn compress(input: &[u8], level: u8) -> Result<Vec<u8>, CompressError>

// Python binding (PyO3)
#[pyfunction]
fn compress(input: &[u8], level: u8) -> PyResult<Vec<u8>> {
    core::compress(input, level).map_err(|e| PyValueError::new_err(e.to_string()))
}
```

Two lines. No logic. Error mapped once, uniformly.

## Multi-Language Consistency

API change lands once → all bindings updated in the same commit. Add one test per
binding that runs the same scenario as the core unit test — proves the map is
correct, not just that it compiles.

## GOOD

Binding is ~20 lines: import, type annotation, one call, error map. Tests call the
same scenario as the core Rust/Go test. Core has zero awareness of the binding.

## BAD

```python
def compress(data: bytes, level: int) -> bytes:
    if not 0 <= level <= 9:          # core already validates this
        raise ValueError("level out of range")
    return _core.compress(data, level)
```

Duplicated precondition. Rust and Python behavior can now drift silently.

## Red Flags

- Binding contains an `if` branch absent from the core.
- Bug reproduced in the JS binding that does not reproduce in the core.
- No binding test running the same scenario as the core unit test.
- Binding error messages differ from core error messages (translation incomplete).
- Binding imports another binding's types instead of the core's types.
