---
id: compile-time-feature-flags
kind: skill
title: Compile-Time Feature Flags
description: >
  Build-time mode switches for optional integrations, heavy deps, or platform
  code. Default build always compiles clean. Matrix-test meaningful combos.
  Distinct from runtime toggles (skill:rollout-and-feature-flags).
applies_when:
  - adding an optional integration or heavy transitive dep
  - platform-specific or no_std code paths
  - creating opt-in extras that most users won't need
  - reviewing a build matrix for completeness
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

# Compile-Time Feature Flags

Build-time mode switches. Not runtime toggles (skill:rollout-and-feature-flags).

## When to Use

Optional integrations, heavy transitive deps, platform-specific code, no_std targets,
or extra compile cost most users don't need. The feature is absent from binaries
that don't opt in.

## Mechanisms by Stack

| Stack   | Mechanism                                                                         |
|---------|-----------------------------------------------------------------------------------|
| Rust    | `Cargo.toml` `[features]` + `#[cfg(feature = "...")]`; `--no-default-features` for `no_std` |
| Python  | `pyproject.toml` `[project.optional-dependencies]` extras                        |
| Node    | `package.json` conditional exports / `optionalDependencies`                       |
| C / C++ | `#ifdef` + CMake `option()`                                                       |

## Default Build Must Be Clean

Default install (no extras) must always work and produce a tested build.
Non-default extras are additive only — never subtractive from the defaults.

## Matrix-Test Meaningful Combos

Test the combinations users would actually enable. Not every permutation.

```yaml
# GitHub Actions matrix
strategy:
  matrix:
    extras: ["", "serde", "full", "serde,async"]
steps:
  - run: pip install -e ".[${{ matrix.extras }}]" && pytest
```

## Dependency Stays Optional

Feature-flagged dep must live under `[project.optional-dependencies]`.
Never unconditional import in the main module; guard with a conditional import block.

## Document the Switches

List flags and what each enables in README and module docs (skill:honest-limits-disclosure).
A user who can't find the knob will reach for an alternative dep instead.

## GOOD

```toml
# pyproject.toml — no hard deps; layered extras opt-in
[project.optional-dependencies]
serde = ["msgspec>=0.18"]
async = ["anyio>=4.0"]
full  = ["mypkg[serde,async]"]
```

Clear layers. Default install has no extras. CI matrix covers `serde`, `async`,
`serde,async`, `full`.

## BAD

Unconditional `import heavy_dep` at the top of a module when `heavy_dep` is used
in one optional code path. Every user pays the compile cost and transitive footprint
whether they use the feature or not.

## Red Flags

- Default install (no extras) fails or is never tested in CI.
- Optional dep imported unconditionally at module top.
- Extra combinations untested; users discover conflicts at their own site.
- README lists no extras; opt-ins are invisible.
- Optional dep imported without a conditional import guard.
