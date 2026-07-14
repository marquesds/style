---
id: xss-and-csp
kind: skill
title: XSS + CSP
description: "Reflected, stored, DOM XSS. Context-aware encoding. CSP depth. Cookie flags. Dangerous sinks."
applies_when:
  - HTML or JS output
  - rich text / user HTML
  - SPA with innerHTML
  - security headers review
agents:
  claude: { kind: skill }
  cursor: { kind: skill, glob: "**/*.{html,htm,js,jsx,ts,tsx,vue,svelte}" }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# XSS + CSP

Untrusted data → document or script context = treat as hostile. skill:injection-defense for SQL/shell; here = browser encoding + sink discipline.

## Classes

- **Reflected**: param echoed once. **Stored**: DB → page every view. **DOM**: JS writes untrusted string into sink (`innerHTML`, `document.write`, `eval`, URL `javascript:`).

## Encoding

Match **context**: HTML body vs attr vs JS vs URL. Framework escapers when correct; never “strip tags” as only defense. **Sink rule**: last hop before browser must be safe — string built in JS then assigned to `innerHTML` still XSS if data untrusted.

## CSP

Content-Security-Policy: default-src backup. **Not** substitute for encode. Prefer nonce/hash for scripts if inline needed. Report-URI/report-to for tuning.

## Cookies

Session cookie: `HttpOnly` + `Secure` + `SameSite` appropriate. Reduces cookie theft via script; does not fix HTML injection into same-origin page.

## Other

- SVG, `href`, event handlers (`onerror`) = attr context.
- JSON in `<script>` = JS context — use `json.dumps` + appropriate type, not manual concat.

## GOOD

Template auto-escapes user name in HTML body; user HTML sanitized with allowlist parser; CSP `script-src` nonce; session `HttpOnly` `Secure`.

## BAD

```html
<div><?= $_GET['q'] ?></div>
```

Reflected XSS. Also: `element.innerHTML = userContent` with no sanitize; “we escape on input” only (output context varies).
