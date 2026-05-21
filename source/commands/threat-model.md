---
id: threat-model
kind: command
title: Threat model current diff or feature
description: >
  Walk STRIDE across trust boundaries in the current diff or feature. Produce a
  flat threat list with element, category, abuse case, and mitigation.
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

Use skill:threat-modeling.

Steps:

1. Identify trust boundaries in the current diff or feature description.
2. Draw a brief text DFD: components, data flows, trust levels on each side.
3. For each element crossing a boundary, walk STRIDE (Spoofing, Tampering,
   Repudiation, Info Disclosure, Denial of Service, Elevation of Privilege).
4. Write one abuse case per applicable STRIDE category.
5. Propose a concrete mitigation per finding; cross-reference
   skill:injection-defense, skill:owasp-top-ten, or skill:defensive-programming
   where relevant.
6. Flag architectural mitigations for an ADR.

Output a flat threat list in this format:

```
Element: <component or data flow>
Boundary: <from> → <to>
S: <abuse case> → <mitigation>
T: <abuse case> → <mitigation>
...
```

Omit STRIDE letters that genuinely do not apply; state why briefly.
