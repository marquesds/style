---
id: tdd
kind: skill
title: TDD
description: >
  Write failing test first. Implementation second. Default test shape is the
  Testing Trophy (static + thick integration + unit + few E2E). Tests are proof,
  not afterthought.
applies_when:
  - new logic
  - bug fix
  - behavior change
  - want proof code works
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

# TDD

Test fail first. Code second. Test pass. Refactor. Repeat.

## Cycle

```text
RED → GREEN → REFACTOR
write failing test → make it pass → clean up → repeat
```

Run suite each step. Green stays green.

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

Bug → reproduction test → confirm fail → fix → confirm pass → run full suite. See skill:bug-first-debugging.

## Testing Trophy (Default)

Broad **static** base (types, lint, contract checks). **Unit** for pure core — fast, narrow. **Integration** band **thick**: real DB / HTTP client / module wiring; fake **only** at true system edge. **E2E** few — critical user journeys only. More confidence from **integration** than from mocked-out “unit” that proves nothing about real seams. See skill:test-design for fan-in ports.

```text
  E2E           ~few     critical paths only
Integration    ~most    real deps; doubles at boundary
Unit           ~some    pure logic, no I/O
Static         ~broad   types, lint, contracts
```

## Good Tests

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

Python: `pytest`, `pytest-asyncio`, `hypothesis`, `freezegun`. Run `pytest -k name` for a single test, `pytest -x` to bail on first fail. Other languages: pick the idiomatic equivalent (`cargo test`, `mix test`, `go test`, `vitest`).

## Red Flags

- Code without tests.
- Test passes on first run before implementation — suspect.
- Bug fix without reproduction test.
- `# noqa`, `@pytest.mark.skip`, or commented-out tests to "pass" the suite.
- Mock returns shaped to make a buggy implementation pass.
