# ADR-0012: Concise technical prose for agent sources

Date: 2026-05-19

Status: Superseded by [ADR-0013](0013-remove-optional-response-skill.md)

Supersedes: [ADR-0003](0003-caveman-voice-for-rules.md)

## Context

ADR-0003 made full caveman voice the default for all files under `source/rules/`,
`source/skills/`, and `source/commands/`. That choice lowered visible output tokens,
but later review showed that most of the gain comes from a simple concise-writing
instruction, not from the full caveman grammar.

[Alex Rios's article, "There is a reason that caveman is a character from the
past"](https://alexriosme.substack.com/p/there-is-a-reason-that-caveman-is)
argues that the honest control is caveman versus a plain concise instruction. The
article also points out a larger cost center: reasoning models can bill hidden
thinking tokens that are not reduced by shortening the visible answer. Anthropic's
[extended-thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)
and [context-window](https://docs.anthropic.com/en/docs/build-with-claude/context-windows)
documentation supports the same cost model: thinking tokens are billed output
tokens, and prior thinking blocks are managed separately from visible conversation
text.

The harness still benefits from concise source files, especially for agents that
merge rules, skills, and commands into one context block. The risk is that full
caveman prose can make security reviews, rollout guidance, and setup instructions
harder to read or easier to misinterpret.

## Decision

Source files now use concise technical prose by default. The style is brief and
direct, but it keeps normal grammar where grammar improves clarity. The preferred
baseline is:

- Be concise and to the point.
- Drop filler and throat-clearing.
- Keep technical terms, identifiers, API names, code blocks, and error strings exact.
- Use full sentences when a fragment could hide sequence, scope, danger, or ownership.
- Prefer clear structure over compressed grammar for reviews, security warnings,
  migrations, rollouts, setup steps, and destructive operations.

The `caveman` skill remains available as an optional response style when the user
explicitly asks for it. It is no longer the authoring rule for source files.

## Consequences

**Positive.** Contributors can edit source files without learning a special register.
Safety-sensitive instructions can carry enough nuance. Agent outputs should still
stay compact because the source now asks for concise prose directly.

**Negative.** Some source files may grow modestly. Merged-agent outputs should be
watched because they still load many files into one block.

**Mitigation.** Keep the 200-line source-file limit, preserve native skill loading
for agents that support it, and measure generated merged-block size when large
rewrites land. Revisit this ADR if merged output grows by more than 20% without a
clear readability or correctness benefit.
