---
id: test-design
kind: skill
title: Test Design
description: >
  What to test, how much, which doubles. Beyond red-green: specs, boundaries,
  mutation thinking, properties. Ties to TDD + testable architecture.
applies_when:
  - new test suite
  - weak assertions
  - choosing mocks
  - shrinking flaky or huge suites
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
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

## GOOD

Parametrize partitions + boundaries; one property for core invariant; fake clock in unit tests.

## BAD

Ten happy-path clones on one partition; suite green but any refactor breaks everything; mock every dependency “for isolation.”
