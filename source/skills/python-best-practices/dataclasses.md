# Dataclasses

Three builders generate the boilerplate of a "data class" — `__init__`,
`__repr__`, `__eq__` — so you never hand-write field-copying constructors.

## Decision Table

| Builder | Mutability | Pick when |
|---|---|---|
| `collections.namedtuple` | immutable | legacy code, tuple compatibility (unpacking, indexing) needed, no type hints |
| `typing.NamedTuple` | immutable | record with type hints that must still *be* a tuple |
| `@dataclass` | mutable by default | the general case: options-rich (`frozen`, `field`, `kw_only`, `__post_init__`) |

Default to `@dataclass`. NamedTuple instances **are** tuples: they compare
equal to plain tuples and unpack positionally — a feature for interop, a trap
for type safety.

## Value Objects: `frozen=True`

`@dataclass(frozen=True)` gives immutability plus a generated `__hash__` —
usable as dict keys and set members, safe to share without defensive copies.
Reach for it for domain value objects (money, coordinates, IDs).

## The Mutable Default Trap

`@dataclass` rejects mutable defaults **at class creation time** — a check the
plain-class equivalent never gets:

```python
@dataclass
class Bus:
    passengers: list[str] = []                       # ValueError at import
    passengers: list[str] = field(default_factory=list)  # GOOD
```

`field()` also carries `repr=False`, `compare=False`, `init=False`, and
`metadata` for per-field tuning.

## Derived Fields: `__post_init__`

Fields computed from other fields go in `__post_init__`, marked
`init=False` so callers can't pass them:

```python
@dataclass
class Order:
    unit_price: Decimal
    qty: int
    total: Decimal = field(init=False)

    def __post_init__(self) -> None:
        self.total = self.unit_price * self.qty
```

In a frozen dataclass, assign via `object.__setattr__(self, "total", ...)`.

## `kw_only=True` (3.10+)

`@dataclass(kw_only=True)` forces keyword arguments — fields with defaults may
then precede required ones, and call sites stay readable past three fields.
Per-field: `field(kw_only=True)`.

## Class Attribute vs Instance Field

In a `@dataclass` body, an annotated name is an instance field; its assigned
value is the per-instance default. An **unannotated** assignment is a plain
class attribute shared by all instances — and `ClassVar[...]` annotations are
explicitly excluded from `__init__`. Don't mix these up: a shared mutable
class attribute masquerading as a field is the bug `default_factory` exists
to prevent.

## Pattern Matching on Instances

Keyword patterns work on any class: `case Point(x=0, y=0)`. Positional
patterns need `__match_args__` — dataclasses and NamedTuples generate it from
field order:

```python
match point:
    case Point(0, 0):
        return "origin"
    case Point(x=0, y=y):
        return f"on y-axis at {y}"
```

## Data Class as Code Smell

A class that is all fields and no behavior may be an anemic model: the logic
operating on those fields is scattered elsewhere as functions taking the
object — low cohesion. Either move the behavior in, or accept the shape
deliberately. Legitimate plain-data uses:

- **DTO / boundary record**: rows from a DB, parsed JSON, API payloads —
  data crossing a boundary *should* be behavior-free.
- **Scaffolding**: a fresh class whose behavior will arrive with the next
  commits.
- **Intermediate**: pipeline stage output consumed immediately.

In this harness, such data bags are exempt from the logic line caps — field
declarations are not complexity (see the Code Quality carve-outs).

## GOOD

```python
@dataclass(frozen=True, kw_only=True)
class Coordinate:
    lat: float
    lon: float

@dataclass
class Cart:
    items: list[str] = field(default_factory=list)
    owner: str = "anonymous"
```

Frozen value object, hashable. Mutable container default via factory.

## BAD

```python
class Coordinate:                      # hand-rolled boilerplate
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
    # no __repr__: <Coordinate object at 0x...>; no __eq__: identity compare

@dataclass
class Bus:
    passengers = []                    # unannotated: shared CLASS attribute,
                                       # silently not a field at all
```

## Red Flags

- Hand-written `__init__` that only copies arguments to attributes.
- `namedtuple` in new code where `typing.NamedTuple` or `@dataclass` fits.
- Mutable default worked around with `= None` inside a dataclass instead of
  `default_factory`.
- Unannotated assignment in a dataclass body intended as an instance field.
- Value object left unfrozen and then used as a dict key.
- Behavior-free class whose "methods" live as free functions mutating it
  everywhere — anemic model, not a boundary DTO.
