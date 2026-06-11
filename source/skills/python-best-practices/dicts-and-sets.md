# Dicts and Sets

Hash tables power dicts and sets. Pick the right missing-key strategy, treat
views as live set-like windows, and let set operators replace loops.

## Building and Merging

- Dict comprehension: `{code: name for code, name in pairs}`.
- Merge (3.9+): `a | b` new dict, `a |= b` in place; right side wins on
  duplicate keys.
- `**` unpacking in literals and calls: `{**defaults, **overrides}`.

## Mapping Pattern Matching (3.10+)

Mapping patterns match **partially by design** — extra keys in the subject are
ignored, no need to enumerate them. Capture the rest with `**extra` if needed.

```python
match record:
    case {"type": "book", "authors": [*names]}:
        return names
    case {"type": "book"}:
        raise ValueError("invalid book record")
```

## Missing Keys: Pick One Strategy

| Situation | Use |
|---|---|
| Read with fallback | `d.get(k, default)` |
| Update a mutable value in place | `d.setdefault(k, []).append(v)` — one lookup |
| Systematic default across the dict | `collections.defaultdict(list)` |
| Custom mapping type | implement `__missing__` (called by `d[k]` only) |

Never the double-lookup dance:

```python
if k in d:            # BAD: looks up k twice, racy in concurrent code
    d[k].append(v)
else:
    d[k] = [v]

d.setdefault(k, []).append(v)   # GOOD: one lookup
```

`defaultdict`'s factory fires only via `d[k]`; `d.get(k)` never creates the
entry. Same for `__missing__`.

## Hashability

A key must be hashable: hash value stable over its lifetime (`__hash__`), and
equality-consistent (`a == b` ⇒ `hash(a) == hash(b)`). All immutable builtins
qualify; a tuple only if everything it holds is hashable. Mutable containers
(`list`, `dict`, `set`) are not. User classes are hashable by identity until
you define `__eq__` — then you must define a matching `__hash__` or instances
become unhashable.

## Views Are Dynamic, Set-Like

`.keys()`, `.values()`, `.items()` return live views — they reflect later
mutations of the dict, no copy made. `.keys()` and `.items()` (with hashable
values) support set operators directly:

```python
stale = cache.keys() - fresh.keys()
shared = a.keys() & b.keys()
```

Don't wrap views in `list()` unless you mutate the dict while iterating.

## Insertion Order

Dicts preserve insertion order (guaranteed since 3.7). Treat it as a
presentation nicety, not algorithmic meaning: if order is part of the logic,
make it explicit (sort, or keep an ordered list of keys alongside). Two dicts
with the same items in different order still compare equal.

## Specialized Mappings and Sets

| Type | Use for |
|---|---|
| `collections.ChainMap` | layered lookups (locals → globals → defaults) without copying |
| `collections.Counter` | tallies; `most_common(n)`; `+`/`-` combine counts |
| `types.MappingProxyType` | read-only facade over a dict you must not let callers mutate |
| `frozenset` | hashable set — set of sets, dict keys, constants |

## Set Ops Replace Loops

Counting hits, intersecting, deduplicating — operators say it in one
expression and run in C:

```python
found = len(needles & haystack)       # not a for-loop with a counter
unique = set(emails)
is_subset = required <= provided.keys()
```

## GOOD

```python
def group_by_ext(paths: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in paths:
        out.setdefault(p.rsplit(".", 1)[-1], []).append(p)
    return out

config = {**defaults, **file_cfg, **cli_overrides}   # rightmost wins
missing = required_fields - payload.keys()
```

## BAD

```python
index = {}
for word in words:
    if word in index:              # double lookup
        index[word] += 1
    else:
        index[word] = 1
# Counter(words) is the whole function

cache[[1, 2]] = "x"                # TypeError: list unhashable
count = 0
for n in needles:                  # loop where `len(needles & haystack)` fits
    if n in haystack:
        count += 1
```

## Red Flags

- `if k in d:` followed by `d[k]` — double lookup.
- Hand-rolled tally loop instead of `Counter`.
- Mutable object used as a dict key or set element.
- `__eq__` added to a key class without `__hash__`.
- Logic depending on dict insertion order without stating it.
- Returning an internal dict where `MappingProxyType` should guard it.
- `list(d.keys())` copies everywhere with no mutation-during-iteration need.
- Membership loops where `&`, `-`, `<=` on sets/views say it directly.
