# ADR-0002: Types-first enforcement of Liskov / Design by Contract

Date: 2026-05-07

## Context

Liskov substitutability is the SOLID principle that pays the most rent in day-to-day work: it pins down what a subclass or implementation is allowed to do without breaking callers. The standard trio of preconditions, invariants, and postconditions makes that constraint precise. The question for a coding-style harness is *how* to enforce them.

Three options were on the table:

1. **Documentation-only.** Write the contract in docstrings (`# Preconditions`, `# Postconditions`, `# Invariants`) and trust authors to honor it. Cheap; entirely unenforced.
2. **Runtime asserts everywhere.** Every public function asserts its preconditions and postconditions. Catches violations in tests and (in production-debug mode) in real traffic. Verbose; cost paid on every call.
3. **Encode contracts in types where the language allows.** Use `NewType`, branded types, refined types, or smart constructors so that an `EmailAddress` is by construction a valid email and a `PositiveInt` cannot be zero or negative. Fall back to runtime asserts only where the type system can't express the invariant. Use property tests to pin behavior across input ranges.

## Decision

Option 3, with explicit fallbacks. The `liskov-and-design-by-contract` skill instructs authors to:

- First reach for the type system. `NewType`, branded types, smart constructors, sealed enums, exhaustive `match`. Validation happens once in the constructor; the rest of the codebase trusts the type.
- Use runtime asserts only when the type system cannot express the invariant (cross-field constraints, balance non-negative across operations, etc.). Asserts state the invariant; they aren't error handling.
- Write property tests with `hypothesis` (or the language's idiomatic equivalent) to demonstrate the contract holds across the input space.

Documentation comes last, not first: a docstring that says "amount must be positive" is worse than a `PositiveInt` parameter, because the docstring is unchecked and `PositiveInt` is.

## Consequences

**Positive.** Contracts are checked statically wherever the type system reaches. Caller code can't pass nonsense without a type error. Property tests catch the cross-field invariants the type system can't express. The dependency graph stays clean — no contract framework, just the language plus one property-testing library.

**Negative.** Languages with weaker type systems (loose dynamic languages, older Python, plain JS) get fewer guarantees from this approach. Authors have to learn the types-first idioms in each language; the skill calls them out, but practice takes time.

**Mitigations.** The skill's GOOD/BAD examples show the most common types-first patterns. Runtime asserts and property tests are explicitly listed as the fallback when types fall short — there's no purity test that forces authors to skip them.
