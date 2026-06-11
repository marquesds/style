# Data Model

Python's data model is a protocol: implement special methods (dunders) and the
interpreter gives your class builtin-like behavior. You implement dunders; you
never call them — the interpreter does, via `len()`, `for`, `in`, `+`, `repr()`.

## Implement, Never Call

| You write | Callers use | Never |
|---|---|---|
| `__len__` | `len(x)` | `x.__len__()` |
| `__getitem__` | `x[i]`, `x[a:b]`, `for`, `in`, `reversed` | `x.__getitem__(i)` |
| `__contains__` | `v in x` | `x.__contains__(v)` |
| `__add__` / `__radd__` | `a + b` | `a.__add__(b)` |
| `__repr__` / `__str__` | `repr(x)` / `str(x)`, f-strings | `x.__repr__()` |

`len(x)` is faster and safer than `x.__len__()`: builtins take C-level
shortcuts and fall back correctly. Calling dunders directly bypasses both.

## `__repr__` vs `__str__` vs `__bool__`

- `__repr__`: unambiguous, for developers — ideally valid constructor syntax
  (`Vector(3, 4)`). Always implement it; it is the debugging surface.
- `__str__`: end-user display. Omit it and `str()` falls back to `__repr__` —
  so `__repr__` alone is enough for most classes.
- `__bool__`: define only when "empty vs non-empty" or "zero vs non-zero" has
  domain meaning. Default falls back to `__len__`; without either, every
  instance is truthy. Never make `__bool__` do work or I/O.

## Sequence Protocol For Free

`__len__` + `__getitem__` alone yield iteration, `in`, `reversed()`, and
slicing — no inheritance, no ABC registration. Duck typing on the protocol.

Make `__getitem__` slice-aware: index returns an item, slice returns an
instance of the **same type**, not a bare `list`.

```python
class Deck:
    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Deck(self._cards[key])  # same type, not list
        return self._cards[key]
```

## `__getattr__` Pitfall

`__getattr__` fires only when normal lookup **fails** — assignment never goes
through it. Expose virtual attributes via `__getattr__` and forget
`__setattr__`, and `v.x = 10` silently creates a shadowing instance attribute:
reads stop reaching `__getattr__`, state forks. Pair them: block or route the
matching writes in `__setattr__`.

## Hashable = `__hash__` + `__eq__` Consistency

Contract: `a == b` implies `hash(a) == hash(b)`, and the hash never changes
during the object's lifetime. Hash from an immutable snapshot of the fields
that define equality (e.g. `hash((self.x, self.y))`). Defining `__eq__`
without `__hash__` sets `__hash__ = None` — instances become unhashable.
Mutable objects should stay unhashable; freeze the fields before hashing.

## Operator Overloading Rules

| Rule | Why |
|---|---|
| Unsupported operand → `return NotImplemented`, never raise | lets Python try the reflected method (`b.__radd__(a)`), raising `TypeError` only after both fail |
| Implement reflected methods (`__radd__`, `__rmul__`, …) | mixed-type expressions where your type is on the right |
| `__add__` returns a **new** object, never mutates `self` | infix operators must not surprise; `a + b` leaving `a` changed is a bug |
| `__iadd__` returns `self` only for **mutable** types | immutable types omit it; Python falls back to `__add__` + rebind |
| `__eq__` falls back gracefully | returning `NotImplemented` from `__eq__` makes Python compare identity, not crash |

```python
class Vector:
    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented  # not raise TypeError
        return Vector(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self + other
```

## GOOD

```python
class Money:
    def __init__(self, cents: int) -> None:
        self.cents = cents

    def __repr__(self) -> str:
        return f"Money(cents={self.cents})"

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.cents == other.cents

    def __hash__(self) -> int:
        return hash(self.cents)
```

Unambiguous repr. `__eq__`/`__hash__` consistent. `NotImplemented` lets
`money == 3` degrade to `False` instead of crashing.

## BAD

```python
class Vector:
    def __add__(self, other):
        self.x += other.x          # mutates self in `a + b`
        return self

    def __eq__(self, other):
        if not isinstance(other, Vector):
            raise TypeError("nope")  # kills `v in list_of_mixed`
        return self.x == other.x     # __hash__ now None: unhashable

n = v.__len__()                      # call len(v) instead
```

## Red Flags

- Direct dunder calls in application code (`x.__len__()`, `x.__getitem__(0)`).
- `__eq__` defined, `__hash__` forgotten — instances silently unhashable.
- Operator method raising `TypeError` instead of returning `NotImplemented`.
- `__add__` mutating an operand or returning `self`.
- `__getattr__` without a paired `__setattr__` guard.
- Slicing a custom sequence returns `list`, breaking method chaining.
- `__bool__` performing I/O or expensive computation.
