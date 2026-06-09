# ADR-0010 — Emit Codex skills in native skill directories

**Status:** Accepted  
**Date:** 2026-05-14  
**Amends:** ADR-0009 for Codex skill placement

## Context

ADR-0009 moved Codex output out of `~/AGENTS.md` and into `.codex/AGENTS.md`, but
kept rules, skills, and commands merged into one managed block. That still bloats
Codex guidance because full skill bodies load with every AGENTS.md read.

Current Codex documentation separates the surfaces:

- `AGENTS.md` carries concise durable guidance.
- `.agents/skills/<id>/SKILL.md` carries reusable workflows loaded through skill
  progressive disclosure.

## Decision

Keep Codex rules and commands in `<root>/.codex/AGENTS.md`, but emit Codex skills
as native skill files at `<root>/.agents/skills/<id>/SKILL.md`.

Prune must cover both surfaces: strip managed blocks from `.codex/AGENTS.md` and
delete managed skill files under `.agents/skills`.

## Consequences

- Codex no longer reads full skill bodies from AGENTS.md on every turn.
- Skill descriptions remain discoverable, include `applies_when` triggers, and full
  instructions load only when Codex selects a skill.
- The Codex adapter is intentionally hybrid: `.codex/AGENTS.md` for durable
  guidance, `.agents/skills` for reusable workflows.
- ADR-0009 still governs the legacy `~/AGENTS.md` cleanup path.
