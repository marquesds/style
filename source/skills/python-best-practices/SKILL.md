---
id: python-best-practices
kind: skill
title: Python Best Practices
description: "Idiomatic Python best practices. Router skill: index of per-topic reference files — data model, sequences, dicts, dataclasses, mutability, functions, type hints, decorators, protocols, iterators, concurrency, metaprogramming. Load only the matching file."
applies_when:
  - writing or reviewing Python code
  - choosing a Python data structure or idiom
  - designing Python classes, protocols, or type hints
  - picking a Python concurrency model
agents:
  claude: { kind: skill }
  cursor: { kind: skill, glob: "**/*.py" }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Python Best Practices

Idiomatic Python guidance, one reference file per topic. Each file is
self-contained: match the task to a row, read **exactly that file** (same
directory as this SKILL.md), apply. Never preload all files.

Canonical source: *Fluent Python*, 2nd ed. (Luciano Ramalho) —
https://pythonfluente.com/2/.

## Index

| Reference file | Read when |
|---|---|
| data-model.md | designing a class others will use like a builtin; `__repr__` / `__len__` / `__getitem__`; operator overloading |
| sequences.md | list/tuple choice; comprehensions vs genexps; unpacking, slicing, sorting; list is not the answer (array, deque) |
| dicts-and-sets.md | dict/set idioms; missing-key handling; views; hashability rules |
| text-and-bytes.md | str vs bytes boundary; encodings; Unicode normalization or comparison |
| dataclasses.md | choosing namedtuple vs `typing.NamedTuple` vs `@dataclass`; frozen, `field()`; data-class smell |
| references-and-mutability.md | aliasing bugs; shallow vs deep copy; mutable default arguments; identity vs equality |
| functions.md | first-class functions; callables; `functools`; replacing Strategy/Command with functions |
| type-hints.md | annotating signatures; `Protocol` in hints; `TypedDict`, overload, variance; gradual typing strategy |
| decorators-and-closures.md | writing decorators; closures, `nonlocal`; `wraps`, `lru_cache`, `singledispatch` |
| classes-and-protocols.md | pythonic object design; ABCs vs protocols vs duck typing; inheritance, mixins, MRO |
| iterators-and-generators.md | iterables vs iterators; generators, `yield from`; lazy pipelines; context managers; `with`/`else`/`match` |
| concurrency.md | threads vs processes vs asyncio; GIL; `concurrent.futures`; asyncio pitfalls |
| metaprogramming.md | dynamic attributes; `@property`; descriptors; `__init_subclass__`; metaclasses |

Two topics overlapping → read both, in index order. General Python style not
listed here → PEP 8 + rule-level guidance applies; do not load any file.

## GOOD

Task: "fix mutable default argument bug" → read `references-and-mutability.md`
only → apply sentinel-default fix. One file loaded, context stays small.

## BAD

Preload all thirteen reference files "for context" before reading the task.
Or skip the index and re-derive Python idioms from memory when a file covers
the exact topic.
