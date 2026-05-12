# ADR-0008: Expand Catalog — Threat Modeling, CI Pipeline, Caching, Rate Limiting

**Date:** 2026-05-12  
**Status:** Accepted

## Context

The skills catalog covered design patterns, testing, SQL, and several security topics
(OWASP, injection defense, XSS), but had no skills for:

- Systematic threat modeling before a feature ships (gap: pre-code security analysis).
- CI pipeline shape: ordering, matrix, caching, secrets hygiene (gap: CI quality kept
  regressing as new workflows were copy-pasted without a reference).
- Application-layer caching: pattern selection, key design, TTL jitter, invalidation
  (gap: repeated cache-poisoning and stampede bugs with no canonical guidance).
- Rate limiting and throttling: algorithm selection, dimensions, 429 contract,
  backpressure (gap: endpoints had global-only limits and missing `Retry-After`).

These four topics each surfaced in post-mortems or code reviews where agents lacked
a named skill to reference.

Two commands were also missing:
- `/threat-model` — invoke the STRIDE walk on the current diff.
- `/refactor` — disciplined single-transformation refactor cycle.

The `refactoring` skill existed; its command did not.

## Decision

Add four skills under `source/skills/`:

- `threat-modeling` — trust-boundary DFD + STRIDE + mitigation decisions before code.
- `ci-pipeline-design` — fail-fast ordering, matrix, cache hygiene, secrets.
- `caching-strategy` — pattern selection, key shape, TTL jitter, singleflight, event
  invalidation. Scope: internal cache only (HTTP caching stays in `restful-http-design`).
- `rate-limiting-and-throttling` — algorithm, dimensions, 429 contract, cost-based
  limits, backpressure.

Add two commands under `source/commands/`:

- `threat-model` — calls `skill:threat-modeling`, produces STRIDE threat list.
- `refactor` — calls `skill:refactoring`, enforces one-transformation-per-commit.

Add four rows to `source/rules/skills-catalog.md` (required by AGENTS.md rule 1).

## Consequences

- Catalog grows from 61 to 65 skills (~7% increase).
- Cross-references increase: `threat-modeling` → `owasp-top-ten`,
  `defensive-programming`, `injection-defense`; `caching-strategy` →
  `unit-of-work-and-transactions`, `n-plus-one-prevention`; `rate-limiting-and-throttling`
  → `resilience-retries`, `restful-http-design`, `defensive-programming`.
- `python -m scripts.lint_source` must exit 0 after this change (verified).
- No existing skills modified; catalog is additive. No breakage for current callers.
