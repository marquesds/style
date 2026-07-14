---
id: liskov-and-design-by-contract
kind: skill
title: Liskov + Design by Contract
description: "Subtypes substitute base types without breaking callers. Encode pre/post/invariants in types where possible. Asserts and property tests fill the gaps. LSP first SOLID principle."
applies_when:
  - new abstract base / Protocol / interface / trait
  - new subclass / impl
  - any function with non-obvious preconditions
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

# Liskov + Design by Contract

Substitutability holds. Contracts encoded in types first, asserts second, prose third.

## The Three Contracts

| Contract | Holds when |
|---|---|
| Precondition | Caller obligations before the call |
| Postcondition | Function obligations after the call |
| Invariant | Always true on the type, in and out |

Subtype rules:

- Precondition: equal or **weaker** in subtype.
- Postcondition: equal or **stronger** in subtype.
- Invariants: preserved.

Break any → not a subtype, even if the type-checker accepts it.

## Types First

Encode contracts in the type system before reaching for `assert`. Refined / branded / `NewType`'d types beat runtime checks because they fail at compile / type-check time.

```python
from typing import NewType
EmailAddress = NewType("EmailAddress", str)   # only valid via constructor
NonEmpty = NewType("NonEmpty", str)
PositiveInt = NewType("PositiveInt", int)
```

Constructor / factory does the validation once; rest of the codebase trusts the type.

## Runtime Asserts as Fallback

When the type system can't express it, assert at the boundary:

```python
def withdraw(account: Account, amount: PositiveInt) -> Account:
    assert amount <= account.balance, "amount exceeds balance"
    new = account.debit(amount)
    assert new.balance >= 0, "invariant: balance non-negative"
    return new
```

Property test the same invariant with `hypothesis`.

## GOOD

```python
class Shape(Protocol):
    def area(self) -> float: ...      # post: result >= 0

@dataclass(frozen=True)
class Square(Shape):
    side: PositiveFloat
    def area(self) -> float: return self.side ** 2

@dataclass(frozen=True)
class Circle(Shape):
    radius: PositiveFloat
    def area(self) -> float: return math.pi * self.radius ** 2

def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)
```

Both subtypes return non-negative. `total_area` works for any shape.

## BAD

```python
class Bird:
    def fly(self) -> None: ...

class Penguin(Bird):
    def fly(self) -> None:
        raise NotImplementedError("penguins don't fly")
```

Subtype strengthens precondition (caller must know it's not a penguin). Code that worked for `Bird` crashes for `Penguin`. LSP violated.

## Property Tests Pin Contracts

```python
@given(side=st.floats(min_value=0.001, max_value=1e6))
def test_square_area_non_negative(side):
    assert Square(PositiveFloat(side)).area() >= 0
```

Hold for every input the strategy generates.

## Red Flags

- Subclass overrides a method with `raise NotImplementedError`.
- Code does `if isinstance(x, ChildClass):` to special-case a "subtype".
- Override widens postcondition (returns `None` where parent never returned `None`).
- Untyped strings flowing through the system, validated at every boundary.
- Comment "do not pass empty list" instead of an `NonEmpty[list[T]]` type.
