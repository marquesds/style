# Metaprogramming

Python lets you customize attribute access and class creation at every level
of power. Power costs readability — solve with the simplest tier and stop.

## The Ladder Rule

| Tier | Reaches | Use for |
|---|---|---|
| plain attribute | one field | default; start here |
| `@property` | one field, one class | compute on access without breaking callers |
| descriptor | one field type, many classes | repeated validation/conversion across fields |
| `__getattr__` | unknown names, one class | dynamic facades, delegation fallback |
| `__init_subclass__` | all subclasses | registration, validation at class creation |
| class decorator | decorated classes | same, opt-in per class |
| metaclass | class creation itself | library-author last resort |

Climb only when the current tier forces duplication. "If you wonder whether
you need a metaclass, you don't" — people who need them know with certainty.

## `@property`: Compute Without Breaking Callers

Start with a public attribute — never preemptive getters/setters. When a read
must compute or a write must validate, swap in a property; call sites don't
change. That deferral is the point: uniform access in both directions.

```python
class Order:
    @property
    def total(self) -> Decimal:
        return sum((i.price for i in self.items), Decimal(0))
```

The same validation on five fields → don't write five properties. Use a
property factory (closure returning `property`) or, cleaner, a descriptor.

## Descriptors

A descriptor is a class with `__get__` / `__set__` whose instances live as
**class** attributes of the managed class. `__set_name__` (3.6+) hands it the
attribute name; store the value in the instance `__dict__` under that name so
each instance keeps its own data and no per-descriptor storage dict leaks
memory.

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be > 0")
        obj.__dict__[self.name] = value

class LineItem:
    price = Positive()
    quantity = Positive()
```

Lookup order: an **overriding** (data) descriptor — has `__set__` — beats the
instance `__dict__`; a **non-overriding** (non-data) descriptor — `__get__`
only — is shadowed by an instance attribute of the same name. That second rule
is why methods work: functions are non-overriding descriptors whose `__get__`
returns a bound method, and why `obj.method = x` can shadow a method.

## `__getattr__` vs `__getattribute__`

`__getattr__` is a **fallback**: invoked only after normal lookup fails. Right
tool for dynamic facades — e.g. wrapping JSON-ish data so `feed.title`
delegates to `feed._data["title"]`. Keep such facades at the boundary
(parsing/IO edge); core logic should use real classes with declared fields.

`__getattribute__` intercepts **every** access, including its own internals —
trivially infinite-recursive, defeats inspection and optimization. Avoid.

```python
class Record:
    def __init__(self, data: dict) -> None:
        self.__dict__["_data"] = data

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name) from None
```

Raise `AttributeError` (not `KeyError`) so `hasattr` and `getattr` defaults
keep working.

## Reflection Toolbox

`vars(obj)` / `obj.__dict__` for the instance namespace; `getattr(obj, name,
default)` / `setattr(obj, name, value)` for name-driven access. Prefer these
over `eval`-style tricks; prefer plain attribute access over them whenever the
name is known at write time.

## Classes Are Objects; Import Time vs Runtime

Class bodies **execute at import**: decorators run, descriptors instantiate,
`__init_subclass__` fires. Function bodies run only when called. Side effects
in class bodies (network, DB, registry mutation beyond the class itself)
make imports slow and order-dependent — keep import time declarative.

## `__init_subclass__` and Class Decorators

Both customize classes without a metaclass, and together they cover nearly
every real need: subclass registries, field validation, auto-generated
methods.

```python
class Plugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, /, key: str, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[key] = cls

class CsvPlugin(Plugin, key="csv"): ...
```

`__init_subclass__` lives in the base and sees every subclass; a class
decorator is explicit opt-in per class. Metaclasses remain for the rare case
of changing how the class object itself is built (e.g. ordered namespaces,
`__call__` interception) — a library-author tool. If you ship one, document
it heavily; debugging metaclass interactions (two bases, two metaclasses)
punishes every downstream user.

## GOOD

Validation needed on three numeric fields across two classes → one `Positive`
descriptor with `__set_name__`, values in instance `__dict__`. Public
attribute `total` later needs computing → becomes a `@property`; zero call
sites change.

## BAD

```python
class Config(metaclass=ValidatingMeta):   # metaclass for two checked fields
    def get_timeout(self):                # Java-style getter, day one
        return self._timeout
```

Getter indirection with no computation; a metaclass doing what one descriptor
(or `__init_subclass__`) does at a fraction of the cognitive cost.

## Red Flags

- Getters/setters written upfront instead of plain attributes.
- Same validation copy-pasted into several properties — descriptor tier missed.
- Descriptor storing values on itself or in a shared dict instead of `obj.__dict__`.
- `__getattribute__` overridden in application code.
- `__getattr__` raising `KeyError`, breaking `hasattr`.
- JSON-facade dynamic attributes leaking from the boundary into core logic.
- Class body performing I/O or heavy work at import time.
- Metaclass where `__init_subclass__` or a class decorator suffices.
