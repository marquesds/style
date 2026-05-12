---
id: honest-limits-disclosure
kind: skill
title: Honest Limits Disclosure
description: >
  State known non-features, constraints, and limitations where readers look first.
  Specific and actionable, not vague. Trade-offs are disclosures too.
  No surprises after adoption.
applies_when:
  - writing a README or module-level doc comment
  - documenting a public library API
  - onboarding users to a system with known constraints
  - a limitation is known but undocumented
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

# Honest Limits Disclosure

State limits where readers look first. Specific. Actionable. No surprises.

## Where to State Limits

README top section, module doc, or the public API's main entry point. Not buried in a
footnote. If the limit affects how a caller uses the system, it must be visible before
they start.

```markdown
## Limitations
- **Not thread-safe.** Wrap in a mutex if shared across goroutines.
- **Single-tenant only.** All state is process-global; use process-per-tenant.
- **No streaming.** Full response buffered; not suitable for >100 MB payloads.
- **MSRV: Rust 1.75.** Older compilers not tested or supported.
```

## What to Disclose

| Category           | Example                                          |
|--------------------|--------------------------------------------------|
| Concurrency model  | "Not thread-safe", "Single-writer"              |
| Scale limits       | Max payload size, max concurrent connections    |
| Platform / runtime | MSRV, Python version floor, OS restrictions     |
| Missing features   | "No streaming", "No i18n", "No pagination"      |
| Known failure modes| "Panics on nil input", "Unbounded growth under X"|
| SLA / support      | "No backward compat guarantee pre-1.0"          |

## Specific, Not Vague

"Not suitable for production" → useless.
"Not thread-safe: wrap in `sync.RWMutex` if shared across goroutines" → actionable.

The reader must know what to do differently, not just that a problem exists.

## Trade-offs Are Disclosures Too

When a design choice has a known cost, state it explicitly: "Uses eager evaluation;
not suitable for infinite sequences." That is a disclosure, not a flaw — it is honest
about the trade-off made (see skill:api-and-interface-design).

## GOOD

```go
// Package set provides an unordered, in-memory set of comparable values.
//
// Not thread-safe. Callers sharing a Set across goroutines must synchronise
// externally (e.g. sync.RWMutex).
//
// Not intended for sets larger than available RAM.
```

Limits visible at the package entry point. No runtime surprises.

## BAD

```go
// Package set provides an efficient generic set.
```

No limits stated. User discovers the thread-safety gap in production load testing.

## Red Flags

- README says "production-ready" without defining what production it is ready for.
- Known performance limit undisclosed; surfaces as a surprise bug report.
- Thread-safety model undocumented; callers assume safe.
- Scale limit documented only in the issue tracker, not the README or module doc.
- "Limitations" section exists but says "none known" when limits are documented elsewhere.
