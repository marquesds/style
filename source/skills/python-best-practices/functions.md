# Functions

Functions are objects: assign them, pass them, return them, store them in
dicts. Most "patterns" that exist to wrap one method in a class collapse into
a plain function. Add a class only when the behavior needs state.

## Higher-Order Built-ins: Modern Replacements

| Legacy call | Prefer | Why |
|---|---|---|
| `map(f, xs)` | `[f(x) for x in xs]` | no lambda needed; reads left-to-right |
| `filter(p, xs)` | `[x for x in xs if p(x)]` | predicate inline |
| `map` + `filter` combo | one listcomp / genexp | single pass, one idiom |
| `reduce(operator.add, xs)` | `sum(xs)` | intent-revealing, faster |
| `reduce(operator.mul, xs)` | `math.prod(xs)` | stdlib since 3.8 |
| `reduce` with boolean ops | `all(xs)` / `any(xs)` | short-circuits |

`functools.reduce` survives only for genuinely custom folds; reach for it last.

## Lambda Discipline

`lambda` earns its keep only as a trivial one-expression argument, typically
`key=`. The moment logic grows — a conditional, a second operation, reuse —
promote it to a named `def`. A name documents and shows up in tracebacks; a
lambda is anonymous noise.

```python
inventory.sort(key=lambda item: item.price)                           # fine
users.sort(key=lambda u: (u.tier or "z", -u.score, u.name.lower()))   # promote
```

## Callables

`callable(obj)` answers "can I call this?" without trying. Python defines nine
flavors of callable; the working summary: user-defined and built-in functions,
bound methods, classes (calling one runs `__new__` then `__init__`), instances
defining `__call__`, and generator / async functions (calling returns a
generator / coroutine instead of running the body). Treat them uniformly:
accept "any callable", never `isinstance(f, types.FunctionType)`.

## `__call__`: Function-Like Objects With State

When a callable must remember things across calls, a class with `__call__`
beats a closure for inspectability — state lives in named attributes:

```python
class RoundRobin:
    def __init__(self, backends: list[str]) -> None:
        self._backends = backends
        self._i = 0

    def __call__(self) -> str:
        backend = self._backends[self._i % len(self._backends)]
        self._i += 1
        return backend
```

## Honest Signatures: `/` and `*`

Positional-only (`/`) and keyword-only (`*`) markers make signatures honest:
callers cannot couple to parameter names you consider internal, and flag-like
arguments cannot be passed as cryptic bare positionals.

```python
def split_exact(value: str, sep: str, /) -> list[str]: ...
def tag(name: str, /, *, cls: str = "", **attrs: str) -> str: ...
```

`tag("p", cls="x")` reads; `tag("p", "x")` fails loudly instead of guessing.

## functools.partial

`partial` adapts arity — fix some arguments, get a narrower callable. Prefer
it over a wrapper lambda when no new logic is added:

```python
from functools import partial
triple = partial(operator.mul, 3)
emit = partial(print, sep="", end="", flush=True)
```

## operator Module Over Trivial Lambdas

| Lambda | Replacement |
|---|---|
| `lambda x: x[1]` | `itemgetter(1)` |
| `lambda r: (r.country, r.city)` | `attrgetter("country", "city")` |
| `lambda s: s.lower()` | `methodcaller("lower")` |
| `lambda a, b: a * b` | `operator.mul` |

`itemgetter` works on anything with `__getitem__`; `attrgetter` follows dotted
paths (`attrgetter("coord.lat")`). All are picklable; lambdas are not.

## Strategy and Command as Functions

A Strategy with one method and no state is a function. Hold strategies in a
module, collect them in a registry, and "pick the best" becomes a `max` over
the registry — no class hierarchy, no `Context` plumbing:

```python
Promotion = Callable[[Order], Decimal]
PROMOS: list[Promotion] = []

def promotion(fn: Promotion) -> Promotion:
    PROMOS.append(fn)
    return fn

@promotion
def bulk_item(order: Order) -> Decimal:
    return sum((li.discount() for li in order.large_lines()), Decimal(0))

def best_promo(order: Order) -> Decimal:
    return max(promo(order) for promo in PROMOS)
```

The registration decorator beats scraping `globals()` for `_promo`-suffixed
names: explicit, no naming convention, strategies can live in any module.
Command collapses the same way — a "command object" with a single `execute()`
is just a callable. Pass the function, a `partial`, or an instance with
`__call__` when undo/state is required. A class-based strategy is still right
when it carries configuration or accumulates state across calls.

## GOOD

```python
def top_earners(staff: Iterable[Employee], n: int, /) -> list[Employee]:
    return sorted(staff, key=attrgetter("salary"), reverse=True)[:n]
```

Named function, positional-only inputs, `attrgetter` instead of a lambda, no
mutation.

## BAD

```python
totals = lambda d: [reduce(lambda a, b: a + b, v) for v in map(lambda t: t[1], d)]
```

Lambda bound to a name, nested lambdas, `reduce` for a sum, `map` where a
comprehension reads. Same logic: `[sum(v) for _, v in d]`.

## Red Flags

- `lambda` assigned to a name — that is a `def` in disguise.
- `reduce` where `sum`, `math.prod`, `all`, `any`, `min`, or `max` fits.
- One-method, no-state class named `*Strategy`, `*Command`, or `*Handler`.
- `lambda x: x[0]` or `lambda x: x.attr` where an `operator` getter fits.
- Boolean argument callers pass as bare `True` — make it keyword-only.
- `isinstance` checks against function types instead of `callable()`.
