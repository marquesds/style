# Decorators and Closures

A decorator is a callable that takes a function and returns a (usually
different) callable, replacing the decorated name. It runs at **import time**;
the decorated function runs at call time. That gap explains both the power
(registration on module load) and the traps (work done too early, state baked
in once).

## Closures Capture Variables, Not Values

A closure holds a reference to the variable, read at call time — not a copy of
the value at definition time. The loop-variable trap:

```python
fns = [lambda: i for i in range(3)]
[f() for f in fns]                       # [2, 2, 2] — all share final i

fns = [lambda i=i: i for i in range(3)]  # default binds value now
[f() for f in fns]                       # [0, 1, 2]
```

Fix with default-argument binding (`i=i`) or `functools.partial`.

## nonlocal

Assignment makes a name local, so rebinding an immutable (int, str, tuple)
from an inner function needs `nonlocal`:

```python
def make_averager() -> Callable[[float], float]:
    count, total = 0, 0.0

    def averager(value: float) -> float:
        nonlocal count, total
        count += 1
        total += value
        return total / count

    return averager
```

Mutating a list or dict needs no `nonlocal` (no rebinding). Two-plus pieces of
closure state → prefer a class with `__call__`; attributes beat cells.

## Always functools.wraps

A wrapper without `@functools.wraps(fn)` destroys the wrapped function's
`__name__`, `__doc__`, and visible signature — breaking tracebacks, `help()`,
and introspection-based frameworks. Non-negotiable in every wrapping decorator.

## Decorator Template

```python
P = ParamSpec("P")
R = TypeVar("R")

def clocked(fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        _report(fn.__name__, time.perf_counter() - t0)
        return result

    return wrapper
```

`ParamSpec` keeps the wrapped signature visible to checkers. Keep wrapper
bodies tiny — push formatting, logging, retry math into named helpers.

## Parameterized Decorators

A decorator taking arguments is a **factory**: calling it returns the real
decorator — three nested levels:

```python
def retryable(attempts: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return _call_with_retry(fn, attempts, args, kwargs)
        return wrapper
    return decorate
```

When three levels read poorly, use a class: `__init__` takes the parameters,
`__call__` takes the function and returns the wrapper. Same contract, flatter.

## Stacking Order

Decorators apply bottom-up: `@a` over `@b` over `def f` means `f = a(b(f))`.
Put framework/registry decorators (e.g. `@app.route`) on top so they register
the fully wrapped function, not the bare one.

## Stdlib First

| Need | Use | Caveat |
|---|---|---|
| memoize a pure function | `functools.cache` | unbounded growth; hashable args only |
| bounded memoization | `functools.lru_cache(maxsize=n)` | hashable args only |
| type-driven dispatch | `functools.singledispatch` | register on ABCs / protocols |

`cache` / `lru_cache` on a **method** keys every entry on `self`: the cache
keeps each instance alive (memory leak) and never shares results across
instances. Cache module-level functions, or hold a per-instance cache built in
`__init__`.

`singledispatch` replaces isinstance ladders with open, type-driven dispatch.
Register implementations against ABCs or protocols (`numbers.Integral`,
`abc.Sequence`), not concretes (`int`, `list`), so compatible future types
dispatch correctly:

```python
@functools.singledispatch
def htmlize(obj: object) -> str:
    return f"<pre>{html.escape(repr(obj))}</pre>"

@htmlize.register
def _(text: str) -> str:
    return f"<p>{html.escape(text)}</p>"

@htmlize.register(numbers.Integral)
def _(n: numbers.Integral) -> str:
    return f"<pre>{n} (0x{int(n):x})</pre>"
```

## Registration Decorators

For plugin / strategy registries the decorator needs no wrapper: record the
function, return it unchanged. No closure, no `wraps`:

```python
HANDLERS: dict[str, Handler] = {}

def handles(event: str) -> Callable[[Handler], Handler]:
    def register(fn: Handler) -> Handler:
        HANDLERS[event] = fn
        return fn
    return register
```

## GOOD

```python
@functools.lru_cache(maxsize=128)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

Stdlib memoization on a pure module-level function with hashable args.

## BAD

```python
def logged(fn):
    def wrapper(*args, **kwargs):
        print(f"calling {fn}")
        return fn(*args, **kwargs)
    return wrapper
```

No `functools.wraps` — name, doc, and signature destroyed. `print` instead of
structured logging. Untyped wrapper hides the real signature from checkers.

## Red Flags

- Wrapping decorator without `@functools.wraps`.
- `lru_cache` / `cache` on an instance method — keeps `self` alive forever.
- Closure over a loop variable without `i=i` or `partial` binding.
- Heavy work (I/O, network) inside the decorator body at import time.
- isinstance ladder where `singledispatch` fits.
- `singledispatch` registered on concrete types instead of ABCs / protocols.
- Registry decorator that wraps when it only needs to record and return.
