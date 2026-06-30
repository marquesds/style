# ADR-0013: Remove optional caveman skill

Date: 2026-06-30

Status: Accepted

Supersedes: [ADR-0012](0012-concise-technical-prose-for-agent-sources.md)

## Context

ADR-0012 moved source authoring to concise normal prose but left the optional
`caveman` skill installed for users who explicitly requested a terse response
mode. That optional skill still created an active route in the skills catalog and
native skill outputs.

The harness goal is now narrower: install engineering practices, not response
personas. Concise prose remains a source-writing rule, but style-mode state is
better left to each agent or user session.

## Decision

Remove the `caveman` skill from `source/skills/`, the skills catalog, and routing
fixtures. Generated agent outputs must not install or advertise a `caveman`
skill.

Historical ADRs remain unchanged except for status links. They record the path
from compressed source prose to concise normal prose, then to removing the
optional skill.

## Consequences

**Positive.** Installed harness output no longer activates or advertises a
persona-style skill. Skill routing stays focused on engineering tasks.

**Negative.** Users who liked the packaged terse response mode must configure it
outside the harness.

**Mitigation.** Keep concise technical prose in source files and generated rules.
If many users ask for the removed skill again, restore it through a new ADR and a
normal skill/catalog/eval change.
