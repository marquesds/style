# ADR-0003: Caveman voice for rules, skills, and commands

Date: 2026-05-07

Status: Superseded by [ADR-0012](0012-concise-technical-prose-for-agent-sources.md)

## Context

Rules, skills, and commands are loaded into an agent's context window every time the agent runs. Even when the agent isn't actively using a particular skill, fragments of nearby text occupy attention budget and shape generation. Token-for-token, every line of preamble in these files is paid for on every prompt.

A typical hand-written engineering doc is fine for humans but fluffy for an LLM: articles, hedging ("really", "basically", "actually"), polite intros, and the implicit thesis-then-restatement structure. The same content compresses to roughly a quarter of the tokens with no loss of technical accuracy if you drop articles, drop filler, allow fragments, and prefer short synonyms.

This style is documented as a Skill called *caveman*. It explicitly preserves identifiers, code, error strings, and quoted text verbatim, so the compression cannot create technical ambiguity inside code blocks or API names.

## Decision

All files in `source/rules/`, `source/skills/`, and `source/commands/` are written in caveman voice (the *full* level: drop articles, fragments fine, short synonyms, no filler). The caveman style applies to body prose, headings, table cells, frontmatter `description`, and `applies_when`.

Caveman voice does **not** apply to:

- Code blocks (GOOD/BAD examples) — written in normal style; agents must render compilable code.
- Quoted error strings, API names, function names — verbatim.
- The README, `docs/style-overview.md`, `docs/contributing.md`, and ADRs — newcomer-facing prose stays normal so a first-time reader can parse it without learning a new register.
- Security or destructive-action warnings inside any file — drop caveman per the caveman skill's Auto-Clarity rule when ambiguity has real cost.

Lint is mechanical (line counts, frontmatter completeness, GOOD/BAD blocks, code-example function length, cross-reference validity). It does **not** try to score caveman density. Voice is a review concern, not a linter rule.

## Consequences

**Positive.** Token budget for the same set of practices drops sharply. Agent recall improves because less noise sits between the agent and the rule. I maintain one register in `source/` and apply it consistently across files.

**Negative.** New contributors need to read the caveman skill before authoring. The voice can feel abrupt; readers used to engineering blog tone may find it terse. Newcomers reading the source files directly miss the on-ramp.

**Mitigations.** `docs/style-overview.md` exists specifically as the on-ramp: the same philosophy in normal English. The README points there before pointing to source files. ADRs (this one included) stay in normal prose so contributors can understand the rationale without first decoding the voice.
