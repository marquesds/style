# Iterators and Generators

Iteration is Python's universal data interface. `for`, comprehensions, unpacking,
`zip`, `sum`, `list(...)` all call `iter()` behind the scenes — implement the
protocol once and every consumer works. Default to lazy generators; materialize
only at the sink.

## Iterable vs Iterator

| Concept | Contract | Lifetime |
|---|---|---|
| Iterable | `__iter__` returns a **new** iterator | reusable; each `for` gets a fresh pass |
| Iterator | adds `__next__`; `__iter__` returns `self` | one-shot; exhausted forever after `StopIteration` |

Never make a class its own iterator over its data. An iterable that returns
`self` from `__iter__` can be traversed once: the second loop sees nothing,
and two concurrent loops corrupt each other's position. Iterable and iterator
are separate roles — let `__iter__` return a generator instead of hand-writing
an Iterator class.

```python
class Sentences:
    def __init__(self, text: str) -> None:
        self.text = text

    def __iter__(self):
        for match in RE_SENTENCE.finditer(self.text):
            yield match.group()
```

No `Iterator` subclass, no index bookkeeping, fresh iterator per loop.

## Generators Replace Iterator Classes

A generator function (`def` containing `yield`) returns a lazy iterator;
the body runs only as values are pulled. Use a generator expression for a
single-use inline pipeline; name it as a generator function once logic grows
or two call sites appear.

`yield from sub` delegates to a sub-iterable: flattening, recursion, and
splitting a pipeline into named stages without a manual `for ... yield` loop.

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item
```

## Stdlib Generator Toolbox

Search `itertools` before writing a loop — the composition is usually there.

| Tool | Use |
|---|---|
| `chain(a, b)` | concatenate iterables lazily |
| `islice(it, n)` / `islice(it, start, stop)` | slice without materializing |
| `takewhile(pred, it)` / `dropwhile` | cut stream on first predicate flip |
| `pairwise(it)` | sliding pairs (3.10+) |
| `product(a, b)` | cartesian product, lazy |
| `groupby(it, key)` | run-length grouping — **input must be sorted by the same key** |
| `map` / `filter` | fine, but a genexp is often clearer |
| `zip(a, b, strict=True)` | 3.10+; raises on length mismatch instead of silent truncation |

`iter(callable, sentinel)` turns any zero-arg callable into an iterator that
stops at a sentinel value: `for block in iter(partial(f.read, 8192), b""): ...`

## Lazy Pipelines End-to-End

Compose generators stage to stage; only the sink (`list`, `sum`, DB write,
file write) materializes. Intermediate `list(...)` calls turn O(1) memory into
O(N) and break streaming — same discipline as the harness streaming rule.

```python
def top_errors(lines, n):
    events = (parse(line) for line in lines)
    errors = (e for e in events if e.level == "ERROR")
    return list(islice(errors, n))  # materialize only at sink
```

## Context Managers

`with` guarantees `__exit__` runs on success, exception, and early return —
use it for every acquire/release pair. `@contextmanager` writes one as a
generator: exactly one `yield`, wrapped in `try/finally` so cleanup survives
exceptions raised in the block.

```python
@contextmanager
def cd(path: Path):
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(prev)
```

3.10+ allows parenthesized multi-context: `with (open(a) as f, open(b) as g):`.

## `else` on for / while / try

`for/else` and `while/else` run the `else` block only when the loop ends
**without** `break` — a search-failed clause, not an "after loop" clause.
`try/else` runs when no exception was raised, keeping the `try` body minimal.
Use sparingly and comment intent (`# else: no match found`); most readers
misparse it.

## match/case Essentials

Guards and OR-patterns keep dispatch flat:

```python
match command.split():
    case ["go", direction] if direction in EXITS:
        move(direction)
    case ["quit" | "exit" | "q"]:
        raise SystemExit
    case _:
        print("unknown command")
```

Patterns destructure sequences, mappings, and class instances; a guard (`if`)
adds the condition a bare pattern cannot express.

## GOOD

```python
def active_emails(rows):
    users = (User(**r) for r in rows)
    return (u.email for u in users if u.active)
```

Lazy end-to-end; caller decides when (or whether) to materialize.

## BAD

```python
class Squares:
    def __init__(self, items):
        self.items, self.pos = items, 0

    def __iter__(self):
        return self          # iterable IS the iterator: one-shot trap

    def __next__(self):
        if self.pos >= len(self.items):
            raise StopIteration
        self.pos += 1
        return self.items[self.pos - 1] ** 2
```

Hand-rolled iterator class; second `for` loop silently yields nothing.
A three-line generator function replaces all of it.

## Red Flags

- Class implements `__next__` and returns `self` from `__iter__` over its own data.
- Hand-written Iterator class where a generator function would do.
- `list(...)` wrapped around every intermediate pipeline stage.
- `groupby` on unsorted input — silently produces fragmented groups.
- `zip` on possibly unequal lengths without `strict=True`.
- Manual `try/finally` open/close where `with` exists.
- `@contextmanager` generator with a bare `yield` not protected by `try/finally`.
- `for/else` used without a comment stating the no-break intent.
