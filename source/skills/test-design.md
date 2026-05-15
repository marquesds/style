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

## Coverage triad

Every behavior under test **must** assert across three angles:

- **Success** — the documented happy path with realistic inputs.
- **Failure** — invalid input, contract violations, dependency errors, raised exceptions.
- **Corner case** — boundaries, empty / null / zero, max size, off-by-one neighbors, concurrency edges.

One angle missing = behavior not pinned. Trivial pure helpers may collapse the three angles into a single parametrized table (see `## Parametrize multiple scenarios`), but all three must be represented. Specification-based partitioning (below) is how you pick the representatives; the triad is the floor for what gets picked.

## Specification-based

Equivalence partitions: pick one representative per class. Boundary values: min, max, just inside/outside, empty, null if allowed. Decision tables for compound rules. Fewer tests, same intent coverage.

## Parametrize multiple scenarios

Behavior with non-trivial input space → parametrize. Single-point happy-path on a behavior that takes varied input is incomplete by construction. One row per partition + boundary (per `## Specification-based`); IDs name each scenario so failures read as a spec line, not "test_double[2]".

```python
import pytest

@pytest.mark.parametrize(
    "value, expected",
    [
        (1, 2),
        (5, 10),
        (10, 20),
    ],
    ids=["positive-small", "positive-mid", "boundary-ten"],
)
def test_double(value: int, expected: int) -> None:
    assert double(value) == expected
```

Split into separate tests when scenarios share **only** the function (different setup, different assertions, different intent) — DAMP wins there. Parametrize when scenarios share **shape** (same arrange/act/assert, varying data).

Stack equivalents: Rust `rstest::rstest` + `#[case]`, JS `it.each` / `test.each`, Go table tests (`for _, tc := range cases`), Elixir `for {input, expected} <- cases, do: test ...`.

Scope: skip parametrize when input space is one (constructor wiring, single-shape adapter glue) — single test reads cleaner.

## Structural feedback

Branch coverage signals missed partitions — not a goal. 100% lines + loose asserts = vanity metric.

## Mutation mindset

If `<` became `<=`, would tests fail? If not, tighten asserts or add boundary case. Tools: `mutmut`, `cosmic-ray`, `pitest`, `stryker` (pick for stack).

## Test doubles

Taxonomy: dummy / fake / stub / mock / spy. Default preference: real impl > fake > stub > mock. Mocks for protocol contracts (“exactly one event published”). State-based assertions > interaction counting unless protocol demands (matches TDD skill).

## Property-based

Assert invariants across generators (`hypothesis`, `quickcheck`, `fast-check`). Pair with examples — not a full replacement.

## Test smells

Hard-coded “now”; unseeded `random` / `uuid4()`; reliance on dict or set ordering; shared mutable fixtures; `if` in test body; asserting private internals; `sleep` for async; giant setup hiding scenario.

## Testability hooks

Inject clock, randomness, I/O ports; keep core pure — see architecture skills above.

## Determinism

Same input + same env ⇒ same outcome, every run, every order. Flaky test is broken test — quarantine, find source, fix; never `@flaky` and move on.

Sources of non-determinism + fix:

- **Clock** — inject `Clock` port (skill:functional-core-imperative-shell). At shell, freeze with `freezegun` / `time-machine`. Equivalents: Rust `mock_instant`, JS `@sinonjs/fake-timers`, Go `clockwork`, Elixir clock injection.
- **RNG** — seed per test; inject `random.Random(seed)` instance, never module-global `random.random()`. Hypothesis: pin `seed=` on flaky-prone strategies.
- **UUIDs** — factory port; deterministic counter or seeded UUID in test.
- **Timezone / locale** — set `TZ=UTC`, `LC_ALL=C` in fixture or `conftest.py`. Format dates with explicit tz, never naive `datetime.now()`.
- **Dict / set ordering** — assert against sorted collections; never snapshot a `set` directly.
- **Hash randomization** — don't depend on `hash()` ordering across runs (`PYTHONHASHSEED`).
- **Filesystem** — `tmp_path` / `tmp_path_factory` with `worker_id`; no `/tmp/foo` literals; no real `~/.config`.
- **Network / DNS** — fake at adapter boundary; no live `httpbin.org`, no real DNS.
- **Concurrency** — no `sleep` for ordering; use barriers / events / deterministic schedulers; assert eventually-consistent invariants with bounded poll + timeout.

```python
def test_session_expires_after_ttl(freezer):
    freezer.move_to("2026-05-15T00:00:00Z")
    s = create_session(ttl=timedelta(minutes=5))
    freezer.tick(timedelta(minutes=6))
    assert s.is_expired()

def test_shuffle_stable_under_seed():
    rng = random.Random(42)
    assert shuffle([1, 2, 3, 4], rng) == [2, 4, 1, 3]
```

Frozen clock + seeded RNG = repro by reading test, not by re-running ten times.

## Afferent coupling and tests

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

Ten happy-path clones on one partition with no failure or corner-case angle for the behavior under test; suite green but any refactor breaks everything; mock every dependency “for isolation.” High fan-in hub: only shallow unit tests + **zero** integration through real wiring; or full E2E replacing integration so every failure is a 10-minute flake. Mocks-only “coverage” on shared semantic surface.

## Red Flags

- Suite covers only the happy path; failure and corner-case angles missing from a behavior under test.
- New behavior shipped with a single assertion on a single representative input.
- Failure tests assert the call raised *something*, not the specific contract violation.
- Corner cases (empty, null, zero, max, boundary neighbors) live only in the developer's head, not the suite.
- Test reads wall clock, unseeded RNG, real network, or relies on dict / set iteration order.
- Flaky test marked `@flaky` / `@pytest.mark.flaky` instead of root-caused.
