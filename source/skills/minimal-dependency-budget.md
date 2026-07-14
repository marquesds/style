---
id: minimal-dependency-budget
kind: skill
title: Minimal Dependency Budget
description: "Each dependency is a tax. Justify against stdlib + transitive footprint before adding. Prefer compact API over many features. Audit and remove when replaceable."
applies_when:
  - adding a new dependency
  - choosing between two libraries
  - reviewing a PR that adds packages
  - auditing dependency hygiene
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

# Minimal Dependency Budget

Each dependency is a tax. Audit before adding one, and remove it when it becomes replaceable.

## Justify Before Adding

Three questions before any new dep:
1. Does stdlib or an existing dep already cover this?
2. What is the transitive footprint (`cargo tree`, `pip show`, `npm ls --depth=1`)?
3. Is maintenance status acceptable (recent commits, responsive maintainers, license)?

Prefer narrow API over many features. A package doing one thing well beats a monolith
that drags 30 indirect deps.

## Audit Commands

| Stack  | Command                              |
|--------|--------------------------------------|
| Rust   | `cargo tree` / `cargo udeps`         |
| Python | `pip show <pkg>`, `pipdeptree`       |
| Node   | `npm ls --depth=1`, `npm audit`      |
| Go     | `go mod graph`, `go mod tidy`        |

Zero direct deps is achievable on many utilities. Prove you need one before adding.

## Transitive Footprint

One dep can bring dozens. Check the full tree, not just the direct import. A dep listed
with "0 dependencies" on its README may resolve 15 at install time.

## Compact API > Feature Count

A dep with 3 stable functions you actually call beats one with 50 that you call 3 of.
More API surface means more churn risk during upgrades.

## Remove When Replaceable

Dependencies accumulate. Audit them once a year. If a dependency does what the stdlib now covers, remove it.
Remove or replace stale, unmaintained, or CVE-flagged dependencies.

## GOOD

```toml
# pyproject.toml — no hard deps in core; consumers opt in via extras
[project.optional-dependencies]
msgpack = ["msgpack>=1.0"]
```

One optional dep, behind an extra. Consumers pay only if they opt in.

## BAD

```python
# requirements.txt
requests   # used for one HTTP call
arrow      # used for one date parse
click      # used for one CLI flag
# each drags 5+ transitive deps
```

All three replaceable with stdlib: `urllib.request`, `datetime`, `argparse`.

## Red Flags

- Dep added "just in case" for a use case that never materialized.
- `npm ls` output spans multiple terminal screens.
- Direct dep unused in any production code path.
- Duplicate-purpose deps coexist (`requests` + `httpx`, `arrow` + `pendulum`).
- Security audit (`npm audit`, `pip audit`) never run.
- Dep added after a 30-second web search with no alternatives considered.
