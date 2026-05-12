---
id: test-design
kind: skill
title: Test Design
description: >
  What to test, how much, which doubles. Default Testing Trophy + fan-in-aware
  rigor. Specs, boundaries, mutation, properties. Ties to TDD + architecture.
applies_when:
  - new test suite
  - weak assertions
  - choosing mocks
  - shrinking flaky or huge suites
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

# Test Design

Builds on [skill:tdd](source/skills/tdd.md). Shape code for seams via [skill:functional-core-imperative-shell](source/skills/functional-core-imperative-shell.md) + [skill:hexagonal-architecture](source/skills/hexagonal-architecture.md).

## Specification-based

Equivalence partitions: pick one representative per class. Boundary values: min, max, just inside/outside, empty, null if allowed. Decision tables for compound rules. Fewer tests, same intent coverage.

## Structural feedback

Branch coverage signals missed partitions — not a goal. 100% lines + loose asserts = vanity metric.

## Mutation mindset

If `<` became `<=`, would tests fail? If not, tighten asserts or add boundary case. Tools: `mutmut`, `cosmic-ray`, `pitest`, `stryker` (pick for stack).

## Test doubles

Taxonomy: dummy / fake / stub / mock / spy. Default preference: real impl > fake > stub > mock. Mocks for protocol contracts (“exactly one event published”). State-based assertions > interaction counting unless protocol demands (matches TDD skill).

## Property-based

Assert invariants across generators (`hypothesis`, `quickcheck`, `fast-check`). Pair with examples — not a full replacement.

## Test smells

Hard-coded “now”; reliance on dict ordering; shared mutable fixtures; `if` in test body; asserting private internals; `sleep` for async; giant setup hiding scenario.

## Testability hooks

Inject clock, randomness, I/O ports; keep core pure — see architecture skills above.

## Afferent coupling and tests

**Afferent** = incoming: others reference this unit ([afferente vs eferente](https://elemarjr.com/livros/arquiteturadesoftware/volume-1/entendendo-e-convivendo-com-o-acoplamento/#Acoplamento_aferente_e_eferente)). High fan-in ⇒ internal bugs and contract drift hurt many consumers — match **rigor** to that blast radius.

- Name the hubs: stable ports, shared abstractions, public SDK surfaces, widely imported types.
- **Behavioral asserts** on what dependents actually observe; interaction-only mocks on semantic hubs hide the contract you owe many callers.
- Abstractions introduced for test seams still gain afferent coupling on the abstraction — pair with regressions + version policy where API is public (skill:api-and-interface-design).
- “Everything mocked” is not coverage for widely referenced pillars.

Abstractions cut static coupling but raise dynamic complexity — tests must pay that down (regressions, mutation where it counts).

## Testing Trophy + High Fan-In

Default distribution ([skill:tdd](source/skills/tdd.md)): **thick integration** at real seams, not mock-heavy “unit” suites that never touch the DB or real adapter. For **high afferent** ports, that integration/contract layer is the main guard — unit tests around pure helpers are not enough. E2E stays sparse.

## GOOD

Parametrize partitions + boundaries; one property for core invariant; fake clock in unit tests. **Trophy:** integration/regression on stable ports many importers share; mutation on that hub when affordable. High fan-in ⇒ behavioral asserts on observed contract, not mocks-only isolation theater.

## BAD

Ten happy-path clones on one partition; suite green but any refactor breaks everything; mock every dependency “for isolation.” High fan-in hub: only shallow unit tests + **zero** integration through real wiring; or full E2E replacing integration so every failure is a 10-minute flake. Mocks-only “coverage” on shared semantic surface.
