---
id: haiku
kind: command
title: Write or refresh the Architecture Haiku
description: >
  Guide through writing or refreshing the Architecture Haiku. Engages
  skill:architecture-haiku. Hard stop if Quality Attributes are not ranked.
agents:
  claude: { kind: command }
  cursor: { kind: command }
  codex:  { section: commands }
  goose:  { section: commands }
  openclaw: { section: commands }
  opencode: { kind: command }
  pi:       { section: commands }
  vibe:   { kind: command }
---

Engage skill:architecture-haiku.

Steps:

1. Ask: is this a new haiku or a refresh of an existing one? If refresh, read the current document first.
2. Fill or update all six required sections: Objective, Functional Requirements, Technical Constraints, Quality Attributes, Design Decisions, Future Plans.
3. **Hard stop**: Quality Attributes must be a ranked numbered list. If the user provides an unranked list, pause and ask them to assign an explicit priority order before continuing.
4. For each Design Decision, confirm it traces back to a specific Quality Attribute rank.
5. Check length: if the document exceeds one page (roughly 60 lines of prose), flag it as too long and propose what to move to a spec or ADR.
6. Output the complete haiku as a fenced markdown block ready to save.

Output: a single `architecture-haiku.md` block. Note any sections still open.
