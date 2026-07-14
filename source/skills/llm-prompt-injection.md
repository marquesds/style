---
id: llm-prompt-injection
kind: skill
title: LLM Prompt Injection
description: "Untrusted text vs system instructions. Tool and RAG boundaries. Least-privilege tools. Do not pipe raw user into privileged prompt."
applies_when:
  - LLM feature with user input
  - RAG over untrusted docs
  - agent with tools
  - system prompt design
agents:
  claude: { kind: skill }
  cursor: { kind: skill }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# LLM Prompt Injection

Model cannot cryptographically separate “system” vs “user” — attacker text can **reinterpret** goals. Treat as **confused deputy** problem, not magic parsing.

## Boundaries

- **System / developer** instructions: fixed strings, not built from user paragraphs.
- **User / document** content: delimit clearly; still assume escape attempts (“ignore above”, fake `</system>`).
- **Output**: model may exfiltrate or format unsafe — validate before side effects.

## Tools and actions

**Trap**: tool args = model output only; user said “call delete with id=ALL”. **Fix**: human confirmation on destructive; skill:api-and-interface-design — server validates authz anyway; tools **narrow** + **typed** arguments; deny broad “run shell” unless isolated.

## RAG

Untrusted corpuses: chunk may contain hostile instructions against assistant. Mitigations: retrieval filters; separate summarization stage with strict schema; cite-only modes; sandbox for code execution (**never** impute).

## Defense depth

Prefer **structured** pipelines (extract → validate schema → act) over one blob prompt. Logging: no pasted API keys into traces (skill:secrets-never-in-repo). Classical injection overlap: skill:injection-defense when model emits SQL/shell.

For product-side design — confidence scoring, structured outputs, fake clients, cost accounting — see skill:llm-system-design.

## GOOD

Fixed system preamble; user content in bounded JSON field; executor checks RBAC before DELETE; destructive tool gated.

## BAD

```text
system = "You help users. " + user_submitted_instructions
tools = [{ "name": "run_sql", "args": "{user}" }]
```

User owns system semantics; arbitrary SQL shaped by model. Injection + confused deputy maximum.
