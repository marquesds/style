---
id: tdd
kind: skill
title: TDD
description: >
  Write failing test first. Implementation second. Default test shape is the
  Testing Trophy (static + thick integration + unit + few E2E). Prefer Chicago
  school: state-based checks, real in-process collaborators, doubles only at
  non-deterministic or external boundaries. Tests are proof, not afterthought.
applies_when:
  - new logic
  - bug fix
  - behavior change
  - want proof code works
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

# TDD

Make the test fail first, write the code second, pass the test, then refactor. Repeat.

## Cycle

```text
RED → GREEN → REFACTOR
write failing test → make it pass → clean up → repeat
```

Run the suite at each step so green stays green.

## Model Every Cycle

Before **each** RED, load skill:spec-driven-development and follow its
Behavioral Modeling Protocol with `workflow=tdd`. Record logical behavior and
create a fresh invocation even for trivial/stateless changes. If Quint is
found, execute fresh `model.qnt`; missing/broken Quint requires explicit
fallback. Never reuse or overwrite prior cycle evidence.

Classify target behavior Added/Removed/Changed/Unchanged. Convert accepted
traces into positive tests, forbidden traces/counterexamples into regression
tests, and invariants into durable contract/property tests. Then start RED.
Model scope is bounded evidence, not implementation equivalence proof.

### RED — Write Failing Test

```python
def test_creates_session_with_defaults():
    store = MemoryStore()
    session = store.create(SessionAttrs(agent_id="agent-1"))
    assert session.status is Status.ACTIVE
    assert session.agent_id == "agent-1"
```

Fails: `create` does not exist.

### GREEN — Minimum to Pass

```python
def create(self, attrs: SessionAttrs) -> Session:
    s = Session(id=SessionId.new(), agent_id=attrs.agent_id, status=Status.ACTIVE)
    self._sessions[s.id] = s
    return s
```

### REFACTOR

Improve shape. Tests stay green. No behavior change.

## Prove-It Pattern (Bug Fixes)

For bugs, write a reproduction test, confirm it fails, fix the root cause, confirm it passes, then run the full suite. See skill:bug-first-debugging.

## Testing Trophy (Default)

Broad **static** base (types, lint, contract checks). **Unit** for pure core — fast, narrow. **No real I/O**: no disk, network, database, or subprocess; in-memory collaborators and fakes only. Incidental **stdout/stderr** (e.g. debug `print`) is fine — still **assert** outcomes. **Integration** band **thick**: real DB / HTTP client / module wiring; fake **only** at true system edge. **E2E** few — critical user journeys only. More confidence from **integration** than from mocked-out “unit” that proves nothing about real seams. See skill:test-design for fan-in ports.

```text
  E2E           ~few     critical paths only
Integration    ~most    real deps; doubles at boundary
Unit           ~some    in-memory; no disk/net/db; print ok
Static         ~broad   types, lint, contracts
```

## Chicago school (default)

Also called **Detroit** style. **Chicago:** drive tests through the **public**
surface; use **real collaborators** in-process when practical; reserve fakes or
mocks for **edges** (I/O, time, third-party APIs). **Prove** real I/O in
**integration** or adapter tests — **unit** stays in-memory or pure. Assert **outcomes and state**,
not who called whom. **London** style — heavy doubles on every neighbor and
interaction assertions — is **not** the default; use it sparingly where a port
contract truly needs it (see skill:test-design). The trophy distribution above
is Chicago school in practice.

## Good Tests

These habits spell Chicago school in day-to-day work.

- State, not interactions: assert outcome, not mock calls.
- DAMP > DRY: each test reads as a complete spec.
- Real impls > mocks for pure logic.
- One assertion per concept; split tests by behavior.
- Descriptive names: reads like the spec.

## GOOD

```python
class TestCompleteSession:
    def test_sets_status_to_completed(self): ...
    def test_returns_error_for_already_completed(self): ...
    def test_returns_error_for_unknown_session(self): ...
```

```python
def test_pricing_rule_uses_line_totals():
    assert price_lines([Line(2, Money.usd("1.50"))]) == Money.usd("3.00")

@pytest.mark.integration
def test_checkout_persists_order(sqlite_uow_factory):
    with sqlite_uow_factory() as uow:
        receipt = checkout(sample_state(), uow)
    assert uow.orders.count() == 1
```

Trophy-shaped: **unit** pins pure rule; **integration** hits real UoW/DB seam (fake only mailer at edge if needed).

## BAD

```python
def test_session_works():
    s = make()
    assert s
```

Vague. Asserts truthiness. Tests nothing useful.

```python
@pytest.mark.integration
def test_everything(playwright_page):
    playwright_page.goto("/")
    # only E2E for business rule; slow, brittle, no seam signal

def test_checkout_only_mocks():
    uow = Mock()
    uow.orders.save = Mock()
    assert checkout(state, uow)  # green while real SQL or transaction bug hides
```

E2E-only for logic **or** checkout proven only with mocks — no real persistence seam.

## Tooling Notes

Python: `pytest`, `pytest-asyncio`, `hypothesis`, `freezegun` / `time-machine`. Run `pytest -k name` for a single test, `pytest -x` to bail on first fail. Other languages: pick the idiomatic equivalent (`cargo test`, `mix test`, `go test`, `vitest`). Tests must be deterministic — freeze clocks, seed RNG, inject UUID/network ports. See skill:test-design `## Determinism`.

For complex rendered or serialized output: use snapshot tests reviewed like code — never auto-accepted (skill:snapshot-testing). For public API functions: pair tests with runnable doc examples (skill:runnable-doc-examples).

## Run Parallel When Safe

Run the suite in parallel by default. It tightens the RED to GREEN loop and uses available cores.

Per stack: `pytest -n auto` (pytest-xdist), `cargo test` (parallel default), `go test ./... -parallel N`, `vitest` (parallel default), `mix test --max-cases N`.

**Serialize only when there is a real race:** shared DB without per-worker schema or transaction, hard-coded port binding, `chdir`, global env mutation, filesystem path collisions, shared monotonic fakes, time freeze that leaks across tests.

Quarantine the offenders, don't downgrade the whole suite: mark them `@pytest.mark.serial`, then `pytest -m "not serial" -n auto` followed by `pytest -m serial -p no:xdist`.

Per-worker isolated databases let suites scale. A session-scoped shared mutable
database makes workers stomp rows and creates false "must be serial" verdicts.

## Red Flags

- Code without tests.
- Test passes on first run before implementation — suspect.
- Bug fix without reproduction test.
- `# noqa`, `@pytest.mark.skip`, or commented-out tests to "pass" the suite.
- Mock returns shaped to make a buggy implementation pass.
- “Unit” test hits filesystem, socket, database, or real HTTP — mark integration or use an in-memory fake.
- Whole suite serialized because two tests can't share a fixture.
- Test depends on a previous test's side effect (ordering coupling masquerading as "needs serial").
- Wall clock / unseeded RNG / live network in a test — non-deterministic by construction.
- TDD cycle started without fresh logical analysis and Quint/fallback evidence.
