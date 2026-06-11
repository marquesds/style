# Sequences

Comprehensions for building, genexps for streaming, tuples for records,
pattern matching for destructuring — and know when `list` is the wrong tool.

## Comprehensions and Genexps

- Listcomp beats `map`/`filter` + `lambda`: one readable expression, no
  callable noise, at least as fast.
- Listcomps have their own scope (3.x): the loop variable does **not** leak.
- Output consumed once or potentially large → genexp, not listcomp. A genexp
  feeds items one at a time; a listcomp materializes everything first.
- Sole argument to a call → drop the extra parens: `sum(x*x for x in v)`.

```python
ascii_sum = sum(ord(c) for c in text if ord(c) < 128)   # streams
codes = [ord(c) for c in text if ord(c) < 128]          # materializes
```

## Tuples: Records and Immutable Lists

- Tuple as **record**: position carries meaning; consume by unpacking
  (`city, year, pop = record`), never by magic indexes scattered around.
- Tuple as **immutable list**: fine, but immutability is reference-only — a
  tuple holding a list can still change content (`(1, [2, 3])` is not
  hashable, not constant). Truly fixed data needs immutable elements.

## Unpacking

| Form | Example |
|---|---|
| Parallel | `lat, lon = coords` |
| Star (any position, once) | `first, *rest = items`; `*init, last = items` |
| Nested | `name, (lat, lon) = ("Tokyo", (35.6, 139.7))` |
| In calls | `fn(*args)`, `[*a, *b]` literals |
| Swap | `a, b = b, a` |

## Sequence Pattern Matching (3.10+)

`match` destructures sequences with structure + guards in one place. Patterns
match `list`, `tuple`, and most sequences — **`str` and `bytes` are excluded**
(they match as atomic values, not item-by-item).

```python
match record:
    case [name, _, _, (lat, lon)] if lon <= 0:
        print(f"{name}: {lat}, {lon}")
    case [name, *_]:
        print(name)
```

## Slicing

- `seq[start:stop:step]`; `seq[::-1]` reverses a copy.
- Name your slices: `SKU = slice(0, 6)`; `line[SKU]` reads as intent,
  `line[0:6]` reads as magic numbers.
- Slices on the left assign in place for mutable sequences: `l[2:5] = [20]`.

## `+`, `*`, and the Aliasing Trap

`+` and `*` always build a **new** sequence. But multiplying a list of
mutable items copies **references**:

```python
grid = [[]] * 3          # BAD: three names for ONE list
grid = [[] for _ in range(3)]  # GOOD: three lists
```

Same trap with `a += b` on a tuple element: `t[0] += [1]` both raises
`TypeError` *and* mutates — avoid mutables inside tuples.

## Sorting

- `list.sort()` sorts in place and returns `None` (Command pattern: in-place
  methods signal "no new object" by returning `None`). Chaining on it is a bug.
- `sorted(iterable)` returns a new list, accepts any iterable.
- `key=` takes a one-argument function: `sorted(words, key=str.casefold)`,
  `items.sort(key=len)`. No comparator functions; build a key instead.
- Python's sort is stable: equal keys keep their relative order — sort by
  secondary key first, primary key second.

## When a List Is Wrong

| Need | Use instead |
|---|---|
| Millions of floats/ints | `array.array` — packed C values, several times less memory |
| FIFO / ring buffer | `collections.deque(maxlen=n)` — O(1) both ends |
| Zero-copy slices of big binary data | `memoryview` |
| Membership tests (`x in s`) | `set` / `frozenset` — O(1) vs list O(n) |
| Numeric crunching | `numpy.ndarray` |

## GOOD

```python
def top_pairs(scores: dict[str, int], n: int) -> list[tuple[str, int]]:
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:n]

first, *middle, last = route
total = sum(price for _, price in cart)   # genexp: no temp list
```

## BAD

```python
result = my_list.sort()        # result is None; wanted sorted(my_list)
board = [["_"] * 3] * 3        # rows alias one list
board[0][0] = "X"              # "changes" every row
names = list(map(lambda u: u.name, filter(lambda u: u.active, users)))
# listcomp says it in half the noise:
# names = [u.name for u in users if u.active]
if item in million_item_list:  # O(n) scan; use a set
    ...
```

## Red Flags

- Chaining on `.sort()` / `.append()` / `.extend()` — they return `None`.
- `[[x]] * n` or `[obj] * n` with mutable `obj`.
- `map`/`filter` + `lambda` where a comprehension is clearer.
- Listcomp built only to be iterated once or fed to `sum`/`any`/`max`.
- Magic index constellations (`row[3]`, `row[7]`) instead of unpacking or
  named slices.
- Giant `list` of numbers where `array.array` fits; `list.pop(0)` in a loop
  where `deque` fits; `in` on a large list where `set` fits.
- `match` pattern expecting to destructure a `str` item by item.
