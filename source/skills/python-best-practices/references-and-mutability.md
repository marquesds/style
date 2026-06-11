# References and Mutability

Variables are labels stuck on objects, not boxes holding them. Assignment
never copies — it binds another name to the same object. Most aliasing bugs
are this one fact, forgotten.

## Labels, Not Boxes

```python
a = [1, 2, 3]
b = a            # b is a: same object, two labels
b.append(4)      # a is now [1, 2, 3, 4]
```

To get an independent object you must copy explicitly. There is no
"assignment by value" mode.

## `==` vs `is`

| Operator | Compares | Use |
|---|---|---|
| `==` | values (`__eq__`) | almost always |
| `is` | identity (same object) | `is None`, module-level sentinels only |

`x is None` is correct because `None` is a singleton. `is` is also right for
your own sentinel objects (`_MISSING = object()`). Everywhere else use `==`.
Never `is` on literals: CPython interns small ints and some strings, so
`a is 256` may be `True` and `a is 257` `False` — implementation detail, not
semantics (CPython itself emits a `SyntaxWarning` for `is` with a literal).

## Copies Are Shallow by Default

`list(l)`, `l[:]`, `dict(d)`, `copy.copy(x)` duplicate the outer container
only — inner objects are shared references. Mutate a nested list through the
"copy" and the original changes too.

`copy.deepcopy(x)` recurses, and handles cycles correctly via its memo dict.
Control depth per class with `__copy__` / `__deepcopy__` when deep-copying
would drag in things that must be shared (sockets, locks, caches).

```python
import copy
inner = [1, 2]
shallow = copy.copy([inner])     # shallow[0] is inner
deep = copy.deepcopy([inner])    # deep[0] == inner, not the same object
```

## Parameters Are Aliases

Python passes by sharing: the parameter is another label on the caller's
object. Mutating a received list/dict/set is visible to the caller. Either
document that the function mutates its argument (and name it accordingly), or
copy defensively at the top: `items = list(items)`. Same discipline when a
class stores a constructor argument: assign a copy unless shared mutable
state is the documented contract.

## Never Mutable Default Arguments

Defaults are evaluated **once**, at `def` time, and stored on the function
object — every call without the argument shares the same list:

```python
def append_to(item, bucket=[]):       # BAD: one bucket for all calls
    bucket.append(item)
    return bucket

def append_to(item, bucket=None):     # GOOD: None sentinel
    bucket = [] if bucket is None else bucket
    bucket.append(item)
    return bucket
```

When `None` is itself a meaningful value, use a private sentinel:
`_MISSING = object()` and test `arg is _MISSING`.

## `del`, Refcounts, and `weakref`

- `del x` removes the **label**, not the object; the object dies only when
  its last reference goes (CPython: refcount hits zero; cycles need the
  generational gc). Don't write logic that depends on *when* destruction
  happens — that is a CPython detail, and `__del__` timing is not portable.
- Caches, registries, and observer lists that must not keep objects alive →
  `weakref`: `WeakValueDictionary` / `WeakKeyDictionary` / `weakref.ref`.
  Entries vanish when the real owner drops the object — no leak, no manual
  unregister. Note basic `list`/`dict`/`int` instances can't be weakly
  referenced; subclasses can.

## Immutables May Share — Don't Care

String interning and small-int caching mean two "different" immutable values
can be the same object (`"a" * 1 is "a"` maybe `True`). Harmless precisely
because immutables can't change under you — but it is why `is` on literals
lies. For immutables, identity is never your business; compare with `==`.

## GOOD

```python
class Bus:
    def __init__(self, passengers: list[str] | None = None) -> None:
        self.passengers = list(passengers or [])   # own copy, own bucket

    def drop(self, name: str) -> None:
        self.passengers.remove(name)               # mutates OUR list only

if result is None:        # identity for the None singleton
    ...
```

## BAD

```python
class TwilightBus:
    def __init__(self, passengers=[]):       # shared default
        self.passengers = passengers          # alias of caller's list!

    def drop(self, name):
        self.passengers.remove(name)          # mutates caller's team list

if name is "admin":                           # identity on a literal
    ...
copy_ = config                                # "copy" that is an alias
copy_["debug"] = True                         # original changed
```

The bus that makes passengers vanish from the caller's roster: alias stored,
mutable default shared, two bugs in two lines.

## Red Flags

- `b = a` on a mutable followed by mutation, expecting independence.
- `is` used for anything except `None` and explicit sentinels.
- `def f(x=[])`, `def f(x={})` — mutable default arguments.
- Constructor storing a passed-in mutable without copying or documenting.
- Shallow copy of nested structures treated as deep.
- Logic relying on `__del__` timing or refcount behavior.
- Long-lived cache/registry holding strong references it never releases —
  `weakref` shaped hole.
- `a is 1000`, `s is "text"` — identity tests on literals.
