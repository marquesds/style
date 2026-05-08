---
id: code-simplification
kind: skill
title: Code Simplification
description: >
  Reduce complexity, preserve behavior. Chesterton's fence.
  Scope to changed code only.
applies_when:
  - code works but reads poorly
  - refactor pass after a feature lands
  - complexity has accumulated
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Code Simplification

Same behavior. Less to read. Less to break.

## Principles

1. **Preserve behavior exactly.** Inputs, outputs, side effects, errors identical. Doubt → don't.
2. **Match project conventions.** Simplification that breaks consistency is churn.
3. **Clarity over cleverness.** Dense one-liner ≠ simple.
4. **Chesterton's fence.** Understand why a thing exists before removing. `git blame` first.
5. **Scope to changed code.** Don't refactor unrelated areas in the same PR.

## Patterns

### Deep Nesting → Match / Early Return

```python
def process(data: Data | None) -> Result:
    if data is None:
        return Result.missing()
    if not data.is_valid():
        return Result.invalid()
    return do_work(data)
```

### Verbose Loop → Comprehension

```python
results = [transform(i) for i in items]
```

### Duplicated Snippet → Helper

```python
def full_name(u: User) -> str:
    return f"{u.first} {u.last}"
```

### Dead Code → Remove

Confirm dead first (`vulture`, `xref`, grep). Ask if unsure. Then delete.

## GOOD

```python
def status(state: State) -> str:
    return {
        State.NEW: "New",
        State.UPDATED: "Updated",
        State.ACTIVE: "Active",
    }[state]
```

Total. Easy to extend. No conditional ladder.

## BAD

```python
def status(state):
    return "New" if state == "new" else ("Updated" if state == "updated" else "Active")
```

Untyped. Ternary nest. Adds a state → rewrite the line.

## Process

1. Read code + tests + `git blame`.
2. Pick **one** simplification.
3. Apply.
4. Run suite. Fail → revert.
5. Commit separately from feature work.
6. Repeat.

## Red Flags

- Simplification needs test edits — behavior changed.
- "Simpler" version is longer than the original.
- Error handling removed for "cleanliness".
- Touching code you don't understand.
- One commit batches a dozen unrelated simplifications.
