---
id: canonical-reference-in-docstrings
kind: skill
title: Canonical Reference in Docstrings
description: >
  Cite the authoritative source in doc comments: math notation, RFC numbers, PEP
  numbers, paper titles. Reduces translation ambiguity for reviewers and agents.
  One-liner citation at the relevant point.
applies_when:
  - documenting an algorithm, protocol, or formula
  - implementing a spec-defined behaviour
  - reviewing code whose correctness depends on an external standard
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Canonical Reference in Docstrings

Cite the authoritative source in doc comments. Reduces ambiguity. Enables verification.

## Why

A citation in a docstring says: this is not invented here — it implements a defined
spec. Human reviewers and agents both benefit from knowing where a concept comes from.
Without a citation, correctness can only be verified by running the code, not by
reading the contract it claims to implement.

## What to Cite

| Origin               | Example                                         |
|----------------------|-------------------------------------------------|
| Mathematical notation| `// Math: S ∩ Z` (set intersection)            |
| RFC / standard       | `// RFC 4122 §4.4 — UUID v4 format`            |
| PEP                  | `# PEP 572 — walrus operator semantics`        |
| Paper / algorithm    | `// Tarjan 1972 — strongly connected components`|
| Protocol doc         | `// MQTT 5.0 §3.1.2 — CONNECT packet layout`   |
| Language spec        | `// ECMA-262 §7.2.14 — abstract equality`      |

## How to Cite

One-liner at the top of the relevant doc comment, or a `References` block for longer
implementations:

```python
def argon2id_hash(password: str, salt: bytes) -> str:
    """Hash password using Argon2id.

    Spec: RFC 9106 §4 — Argon2id variant.
    Math: m=65536, t=3, p=4 per §4 recommended values.
    """
```

Pair with skill:source-driven-development: citation confirms the installed version was
consulted, not memory.

## Citations ≠ Copies

Cite the source; do not reproduce protected text. A short notation or formula plus a
reference identifier is enough.

## GOOD

Docstring for `Intersection` includes `// Math: S ∩ Z`. Docstring for UUID v4
generation cites `RFC 4122 §4.4`. Reviewer can verify the implementation against
the spec without tracing down the original requirement.

## BAD

```python
def argon2id_hash(password: str, salt: bytes) -> str:
    """Hash password."""
```

No spec citation. Reader does not know which Argon2 variant, which parameter values,
or how to verify the implementation is correct.

## Red Flags

- Cryptographic or encoding function with no RFC / spec citation.
- Algorithm whose correctness is tribal knowledge not visible in the code.
- Doc comment cites an internal wiki page or a Slack thread — not durable.
- Copy-paste implementation from a web search with no original reference.
- Math-heavy formula in code with no notation or paper citation.
