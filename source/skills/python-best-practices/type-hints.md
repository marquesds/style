# Type Hints

Gradual typing: annotate where annotations pay rent. Hints are read by checkers
(mypy, pyright) and humans — the interpreter ignores them at runtime. An
annotated signature that lies is worse than no annotation.

## Gradual Typing Strategy

| Surface | Annotate? |
|---|---|
| Public function / method signatures | always |
| Module boundaries, ports, adapters | always |
| Dataclass / TypedDict fields | always |
| Internal helpers | optional — often inferable |
| Local variables | rarely — only when inference fails |

Annotate boundaries first; let inference carry internals. Run the checker in
CI or the hints rot into wishful comments.

## Modern Syntax (3.10+)

`list[str]`, `dict[str, int]`, `tuple[int, ...]` — not `typing.List`.
`X | None` — not `Optional[X]`; `int | str` — not `Union[int, str]`.
`Optional` never meant "optional argument": it means "or None", and every
`X | None` obligates an explicit `is None` branch in the caller. Don't default
parameters to `None` just to dodge picking the real type.

## Accept Abstract, Return Concrete

Parameters: the widest type supporting the operations you actually perform —
`abc.Iterable` if you only loop, `abc.Sequence` if you index, `Mapping` not
`dict`. Returns: the precise concrete type, so callers know what they hold.

```python
def dedupe(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))
```

`items: list[str]` would reject tuples, generators, and dict views — for
nothing. Surface design rules: skill:api-and-interface-design.

## Duck Typing, Statically: Protocol

Nominal typing (inheritance, `isinstance`) demands implementers name you.
`Protocol` types the duck: structure decides. Define the protocol on the
**consumer** side, minimal — only the methods the consumer calls:

```python
class SupportsClose(Protocol):
    def close(self) -> None: ...

def shutdown(resources: Iterable[SupportsClose]) -> None:
    for r in resources:
        r.close()
```

`@runtime_checkable` permits `isinstance(x, SupportsClose)`, but it only
checks that the method names exist — not signatures, not return types. Treat
it as a smoke test, never as input validation.

## TypedDict for JSON-Shaped Boundaries

```python
class BookDict(TypedDict):
    isbn: str
    title: str
    authors: list[str]
    pagecount: NotRequired[int]  # 3.11+, or typing_extensions on 3.10
```

A `TypedDict` is a plain `dict` at runtime — zero enforcement. It documents
the shape for the checker at JSON boundaries; data crossing a trust boundary
still needs real validation (pydantic, manual checks). Promote to `@dataclass`
once behavior attaches to the data.

## @overload

When the return type depends on argument types, one honest signature is
impossible — declare each shape, implement once:

```python
@overload
def fetch(key: str) -> Record: ...
@overload
def fetch(key: None) -> None: ...
def fetch(key: str | None) -> Record | None:
    return _lookup(key) if key is not None else None
```

## TypeVar

```python
T = TypeVar("T")

def first(seq: Sequence[T]) -> T:
    return seq[0]

RealT = TypeVar("RealT", bound=numbers.Real)   # bounded: any Real subtype
StrOrBytes = TypeVar("StrOrBytes", str, bytes)  # constrained: closed set
```

A bare `TypeVar` links parameter and return so the input type flows through;
`bound=` caps it at a supertype; constraints restrict to an exact closed set.

## Variance in One Paragraph

Mutable generics are **invariant**: `list[Sub]` is *not* a `list[Base]` — code
holding it as `list[Base]` could append a sibling subtype and corrupt the
caller's list. Read-only containers and return positions are **covariant**:
`Sequence[Sub]` substitutes for `Sequence[Base]`. Argument positions are
**contravariant**: a callable accepting a broader type substitutes for one
accepting a narrower — `Callable[[Base], X]` is accepted where
`Callable[[Sub], X]` is expected. Rule of thumb: values you take out →
covariant; values you put in → contravariant; both → invariant. The deeper
substitutability rules: skill:liskov-and-design-by-contract.

## Any Is a Contagion

`Any` is bidirectionally compatible with everything, so it disables checking
on every expression it touches and spreads silently through assignments and
returns. If you mean "any object that I don't inspect", say `object` — the
checker then rejects accidental attribute access. Reserve `Any` for genuine
dynamic escape hatches, kept at the boundary.

Don't fight the checker: a chain of `cast()` calls or stacked `# type: ignore`
means the design lies about its types. Restructure — narrow with `isinstance`,
split the function, fix the protocol — instead of overriding the verdict.

## GOOD

```python
def total_pages(books: Iterable[BookDict]) -> int:
    return sum(b.get("pagecount", 0) for b in books)
```

Abstract parameter, concrete return, TypedDict keys checked statically.

## BAD

```python
def process(data: Any) -> Any:
    return data["items"][0].name.upper()
```

`Any` in, `Any` out: every access unchecked, every caller infected.

## Red Flags

- Public function left untyped in an otherwise annotated module.
- `list[X]` / `dict[K, V]` parameter where `Iterable` / `Mapping` suffices.
- `X | None` return that no caller checks for `None`.
- `Any` outside an explicit, commented boundary.
- `cast()` applied more than once along the same value's path.
- `runtime_checkable` isinstance used as validation of untrusted input.
- `typing.List`, `Union[X, Y]`, `Optional[X]` in new 3.10+ code.
- Protocol defined next to the implementer with every public method listed.
