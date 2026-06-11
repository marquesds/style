# Classes and Protocols

Design objects that behave like the builtins users already know, expose the
narrowest honest interface, and inherit only from things meant to be inherited.

## Pythonic Object Checklist

| Member | When |
|---|---|
| `__repr__` | always — unambiguous, ideally round-trippable |
| `__eq__` + `__hash__` | as a pair; defining `__eq__` alone makes the class unhashable |
| `__format__` | user-facing values needing display variants |
| `from_*` classmethods | alternative constructors |
| `__slots__` | proven memory need only |

Alternative constructors are `@classmethod`s returning `cls(...)` — not bare
functions — so subclasses construct themselves:

```python
@classmethod
def from_iso(cls, text: str) -> "Span":
    start, _, end = text.partition("/")
    return cls(datetime.fromisoformat(start), datetime.fromisoformat(end))
```

`__slots__` saves memory only at scale (millions of instances — measure
first). It breaks dynamic attribute assignment and weak references unless
`"__weakref__"` is declared, and every subclass must re-declare its own slots
or the per-instance `__dict__` quietly returns.

## Private: `_x` vs `__x`

`_x` is convention: "internal, no contract". `__x` triggers name mangling to
`_Cls__x` — protection against *accidental* clobbering in subclasses, not
security; anyone can still reach it. Default to `_x`; mangle only when a
subclass attribute collision is a realistic hazard (framework base classes).

## Four Kinds of Interface

| Kind | Mechanism | Checked |
|---|---|---|
| duck typing | just call the method | runtime, on use |
| goose typing | ABC + `isinstance` against the ABC | runtime, explicit |
| static duck typing | `Protocol` | static |
| static nominal | concrete classes + inheritance | static |

Duck typing is the default. Goose typing rule: `isinstance` against **ABCs
only** (`abc.Sequence`, `numbers.Real`), never against concrete classes —
checking concretes closes the door structural typing exists to open. Choose
`Protocol` when implementers are third-party or out of your control; choose an
ABC when you need inherited concrete methods (template method) plus virtual
`register`. Monkeypatching a class to make it fit an interface is a test-suite
technique, never production design. Surface shape rules:
skill:api-and-interface-design.

## Inheritance Discipline

Subclassing builtins (`dict`, `list`, `str`) is broken by design: their C-level
methods skip your overrides — `dict.update` never calls your `__setitem__`,
`dict.__init__` ignores it too. Subclass `collections.UserDict`, `UserList`,
`UserString` instead; they route everything through the Python-visible methods.

Inherit from ABCs and protocols, not concrete classes. Heuristic: **all
non-leaf classes should be abstract** — if you subclass a concrete class,
extract the shared abstract base instead. Substitutability contract for every
subclass: skill:liskov-and-design-by-contract. Past two layers of inheritance,
reach for composition: wrap, delegate, expose only what callers need.

## Mixins

A mixin bundles one focused behavior, is named `*Mixin`, is never instantiated
alone, and is never the only base class. A "mixin" carrying state and three
responsibilities is just a bad base class.

## MRO and Cooperative super()

`super()` follows the class's MRO (`Cls.__mro__`), not "the parent" — in
multiple inheritance the next class in line may be a sibling. Cooperative
methods accept `**kwargs` and always forward, so every class in the MRO gets
its turn:

```python
class UpperCaseMixin:
    def __setitem__(self, key: str, value: object) -> None:
        super().__setitem__(key.upper(), value)

class UpperDict(UpperCaseMixin, collections.UserDict):
    """Mixin first: MRO puts it before UserDict."""
```

Mixin order matters: bases listed left of the target class run first.

## GOOD

```python
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    @classmethod
    def from_hex(cls, text: str) -> "Color":
        n = int(text.removeprefix("#"), 16)
        return cls(n >> 16 & 0xFF, n >> 8 & 0xFF, n & 0xFF)

    def __format__(self, spec: str) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
```

Frozen dataclass: `__repr__`, `__eq__`, `__hash__` generated consistently.
Alternative constructor via `cls`. Display logic in `__format__`.

## BAD

```python
class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)
```

Subclasses `dict` directly: `CaseInsensitiveDict(A=1)`, `.update(B=2)`, and
`setdefault` all bypass the override in CPython's C code paths. Use
`collections.UserDict`, which routes through `__setitem__`.

## Red Flags

- `__eq__` defined without `__hash__` on a class used in sets or dict keys.
- `__slots__` added "for speed" with no memory measurement, or missing in a
  subclass of a slotted class.
- `isinstance` against a concrete class where an ABC or Protocol exists.
- Direct subclass of `dict` / `list` / `str` overriding item access.
- Concrete class subclassing another concrete class — extract the ABC.
- Mixin with `__init__`, state, or more than one behavior.
- `super().__init__()` calls that drop `**kwargs` in a cooperative hierarchy.
- Production monkeypatch to retrofit an interface.
