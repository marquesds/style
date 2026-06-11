# Text and Bytes

`str` is a sequence of Unicode code points; `bytes` is a sequence of integers
0–255. They are different types with different semantics — never mix them.

## The Unicode Sandwich

Decode on the way in, process as `str`, encode on the way out. Bytes exist
only at the I/O boundary; everything inside the program is text.

```text
bytes  --decode-->  str (all business logic)  --encode-->  bytes
   input boundary                                output boundary
```

`str` has no `.decode()`; `bytes` has no `.encode()` you should be using in
logic. A `bytes` leaking into string formatting yields `"b'...'"` garbage in
output — that is the sandwich violated. Boundary placement is the same move as
skill:functional-core-imperative-shell — conversion is shell work.

## Always Pass `encoding=`

`open()` without `encoding=` uses a **locale-dependent platform default**
(UTF-8 on most Linux/macOS, legacy code pages on Windows). Code that works on
the dev box corrupts on the next machine.

```python
open(path, encoding="utf-8")             # text, explicit
open(path, "rb")                         # binary: bytes, no decoding
open(path, encoding="utf-8", errors="replace")   # tolerate damage, visibly
```

| `errors=` | Behavior | Use when |
|---|---|---|
| `strict` (default) | raise | data must be valid — fail loudly |
| `replace` | `�` / `?` | display pipelines; loss is visible |
| `ignore` | drop silently | almost never — silent data loss |
| `backslashreplace` | `\xNN` escapes | debugging/logging raw content |

## Diagnosing Unicode Errors

| Error | Meaning | Typical cause |
|---|---|---|
| `UnicodeDecodeError` | bytes → str failed | wrong `encoding=` for the input; binary read as text |
| `UnicodeEncodeError` | str → bytes failed | target codec can't represent the char (e.g. `é` → ASCII) |
| `SyntaxError: Non-UTF-8 code` | source file itself | .py saved in legacy encoding |

Don't guess-and-retry codecs in a loop; identify the real source encoding
(metadata, spec, or `chardet`-style detection at the boundary, once).

## Normalize Before Comparing

The same visible text has multiple code-point spellings: `"café"` as 4 code
points (NFC) or 5 (NFD, `e` + combining accent). `==` compares code points, so
visually identical user input can compare unequal.

```python
from unicodedata import normalize

def nfc_equal(a: str, b: str) -> bool:
    return normalize("NFC", a) == normalize("NFC", b)
```

Normalize to **NFC** at the input boundary (forms K — NFKC/NFKD — are lossy;
only for search/indexing, never for storage). For caseless matching use
`str.casefold()`, not `lower()`: casefold handles `ß` → `ss` and ~hundred
other mappings that `lower()` misses. Combine: normalize then casefold.

## Sorting Human Text

Default `sorted()` orders by code point: `"caju" < "cajá"` fails Brazilian
expectations, uppercase sorts before lowercase. Correct collation needs
`locale.strxfrm` as key (after `setlocale`, process-global and OS-dependent)
or the `pyuca` library (pure Python, Unicode Collation Algorithm, no locale
state). For user-facing sorted lists, code-point order is a bug.

## Dual-Mode APIs

`re` and `os` accept both `str` and `bytes` — with different behavior:

- `re` patterns: `str` patterns match Unicode digits/words/spaces for
  `\d \w \s`; `bytes` patterns match ASCII only. Pattern and subject must be
  the same type.
- `os.listdir(".")` → `str` names (surrogate-escaped if undecodable);
  `os.listdir(b".")` → raw `bytes`. Use bytes mode to survive hostile
  filenames; `os.fsencode`/`os.fsdecode` convert at the edge.

## GOOD

```python
def load_names(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [normalize("NFC", line.strip()) for line in f]

def caseless_eq(a: str, b: str) -> bool:
    fold = lambda s: normalize("NFC", s).casefold()
    return fold(a) == fold(b)
```

Explicit codec. NFC at the boundary. Casefold for caseless match.

## BAD

```python
def load_names(path):
    with open(path) as f:              # platform-default codec
        return f.read().split("\n")

if user_input == stored_name:          # unnormalized comparison
    ...
if name.lower() == other.lower():      # lower() misses casefold mappings
    ...
data = socket.recv(1024)
print("got: " + data)                  # TypeError / b'...' leak: str + bytes
```

## Red Flags

- `open()` for text without `encoding=`.
- `bytes` appearing in business logic or string formatting (`b'...'` in output).
- `errors="ignore"` anywhere near persistent data.
- User-input comparison without NFC normalization.
- `lower()` used for caseless matching.
- Code-point `sorted()` on human-facing names in a localized product.
- `try` codec A `except` codec B chains instead of finding the real encoding.
- Mixing `str` pattern with `bytes` subject in `re`.
