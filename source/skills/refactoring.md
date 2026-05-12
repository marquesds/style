---
id: refactoring
kind: skill
title: Refactoring
description: >
  Behavior-preserving structural change. Fowler's discipline when tests exist;
  Feathers' Legacy Code Algorithm when they don't. Named transformations catalog.
  Two hats: never mix refactoring with feature work.
applies_when:
  - structural change without behavior change
  - extracting, inlining, or moving code
  - working with code that has no tests
  - code smells found during review
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

# Refactoring

Behavior-preserving structural change. Tests before, tests after, green at every step.
For narrow cleanups inside tested code see skill:code-simplification. Regression pinning
for bugs see skill:bug-first-debugging.

## Two Modes

| Mode | First move |
|------|-----------|
| **Fowler** — tests exist | Pick one named refactoring; run suite; repeat |
| **Feathers** — no tests | Identify seam → write characterization test → then change |

Never skip to "Fowler mode" on untested legacy code. Feathers first.

## Fowler's Discipline

Tiny, behavior-preserving steps. Run the full suite after each step.

Two hats rule: never wear both at once. Refactoring hat = only structural change,
no new behavior. Feature hat = behavior change, no restructuring. Mixed-hat commits
hide behavioral drift. Split them.

## Named Refactorings (catalog)

| Refactoring | Trigger |
|-------------|---------|
| Extract Function | block reads as a comment ("# do the X thing") |
| Inline Function | body obvious; name adds no value |
| Extract Variable | complex expression used twice or more |
| Rename | name doesn't match what it does |
| Move Function | function uses more of another module's data |
| Move Field | field accessed more by another class |
| Replace Temp with Query | temp assigned once; used in multiple places |
| Replace Conditional with Polymorphism | repeated type switches |
| Replace Magic Literal | bare constant with no name |
| Split Phase | function does sequential steps that need different data |
| Combine Functions into Class | several functions share same input data |
| Replace Parameter with Query | parameter derivable from object the caller holds |
| Encapsulate Variable | public field mutated by many callers |
| Encapsulate Collection | callers modify collection directly |

## Code Smells → Refactoring

| Smell | Resolution |
|-------|-----------|
| Mysterious Name | Rename |
| Duplicated Code | Extract Function |
| Long Function | Extract Function, Split Phase |
| Long Parameter List | Replace Parameter with Query, Combine Functions into Class |
| Global Data | Encapsulate Variable |
| Mutable Data | Encapsulate Variable, Encapsulate Collection |
| Divergent Change | Split Phase, Extract Function |
| Shotgun Surgery | Move Function, Move Field |
| Feature Envy | Move Function |
| Data Clumps | Combine Functions into Class |
| Primitive Obsession | Replace Magic Literal, Extract Variable |
| Repeated Switches | Replace Conditional with Polymorphism |
| Lazy Element | Inline Function |
| Speculative Generality | Inline Function, Remove dead parameter |
| Message Chains | Move Function (hide traversal behind owner) |
| Middle Man | Inline Function |
| Comments as Deodorant | Extract Function (name it what the comment said) |

## Feathers' Legacy Code Algorithm

1. **Identify change points** — exactly which lines must change.
2. **Find test points** — where can you sense the behavior without changing more?
3. **Break dependencies** — introduce a seam so the unit is testable in isolation.
4. **Write characterization tests** — pin existing behavior (bugs included).
5. **Make the change** — now wearing Fowler's hat; suite green at every step.
6. **Deduplicate** — extract common structure revealed by the change.

## Characterization Tests

Pin existing behavior before touching anything. Different from spec tests (which
assert desired behavior) and regression tests (which pin a fixed bug). A
characterization test says: "this is what it does right now — alert me if I change it."

```python
def test_calculate_total_current_behaviour():
    """Characterization: pins output before refactoring discount branch."""
    result = calculate_total(items=[Item("X", 10)], promo="SUMMER10")
    assert result == 9  # existing output; may not be "correct" — that's ok
```

## Seams

Seam = place to alter behavior without editing the production code. Pick the
weakest seam that isolates the change.

**Object seam** (prefer): subclass + inject, or pass a collaborator as parameter.

```python
class LegacyReporter:
    def send(self, msg: str) -> None:
        smtp_blast(msg)  # untestable

class FakeReporter(LegacyReporter):
    def send(self, msg: str) -> None:
        self.sent.append(msg)

def process(reporter: LegacyReporter = LegacyReporter()) -> None:
    reporter.send("done")
```

Inject `FakeReporter` in tests. Production default unchanged.

## Sprout and Wrap

When surrounding code is too tangled to characterize fully:

**Sprout**: write new logic in a brand-new function, call it from the legacy site.
Tests cover only the sprout. Legacy code untouched.

**Wrap**: write a new function that delegates to the legacy method plus adds the
new behavior around it. Tests cover the wrapper.

```python
def legacy_export(path: str) -> None: ...  # untested, tangled

def export_with_audit(path: str, audit: AuditLog) -> None:
    legacy_export(path)
    audit.record("exported", path)
```

Tests exercise `export_with_audit` with a fake `AuditLog`. Legacy untouched.

## GOOD

```python
# Step 1: characterization test
def test_discount_current_output():
    assert calculate_total([Item("A", 100)], "VIP") == 80

# Step 2: Extract Function — discount logic isolated
def _apply_vip_discount(subtotal: float) -> float:
    return subtotal * 0.8

def calculate_total(items: list[Item], promo: str) -> float:
    subtotal = sum(i.price for i in items)
    return _apply_vip_discount(subtotal) if promo == "VIP" else subtotal
```

Suite green after each step. One named refactoring at a time.

## BAD

Rewrite `calculate_total` end-to-end in one diff ("looked messy"), no characterization
test, behavior silently shifts for edge cases. "No behavior change" — but nothing proves
it.

## Red Flags

- "Big refactor" branch open more than one week.
- Mixed-hat commit: "refactor + feature" in same diff.
- Refactoring without tests — characterization or otherwise — in place first.
- Renaming inside a 500-line function nobody has characterized.
- "No behavior change" claim with no green suite to back it.
