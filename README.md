# style

A language-agnostic, single-source-of-truth coding-style harness. Captures my own practices (TDD, bug-first, minimal hexagonal, functional core / imperative shell, types-first LSP, RESTful HTTP, observability, perf budgets, conventional commits + feature flags) and feeds them into any AI coding agent: Claude Code, Cursor, Codex, Vibe.

## Install

```bash
git clone https://github.com/<you>/style ~/.style
cd ~/.style
./install.sh                   # installs into all detected agents
./install.sh --agent claude    # only one agent
./install.sh --dry-run         # show what would change, write nothing
```

The installer writes only into a managed namespace inside each agent's config directory (`~/.claude/skills/`, `~/.cursor/rules/`, etc.) and never clobbers files outside it. Re-running is idempotent.

## What gets installed

| Bucket | What it is | Where it ends up |
|---|---|---|
| Rules (`source/rules/`) | Always-on guidance: workflow, code quality, design principles, observability | Cursor `.mdc` rule files; Claude `CLAUDE.md` managed section; Codex `AGENTS.md` managed section |
| Skills (`source/skills/`) | On-demand expertise: TDD, bug-first, hexagonal, LSP/DbC, REST, UoW, code review, etc. | Claude `~/.claude/skills/<id>/SKILL.md`; Cursor `.mdc` with description-based loading; Codex `AGENTS.md` |
| Commands (`source/commands/`) | Slash-command prompts: `/spec`, `/plan`, `/tdd`, `/bug`, `/review`, `/done`, `/commit` | Claude `~/.claude/commands/`; Cursor `~/.cursor/commands/` |

## Voice

All `source/rules/`, `source/skills/`, `source/commands/` content is written in **caveman style** to cut tokens roughly 75% while keeping technical accuracy: drop articles, drop filler, fragments OK, short synonyms. Code examples stay normal. README, `docs/`, and ADRs stay normal prose.

If caveman bothers you, read `docs/style-overview.md` first — it explains the same philosophy in normal English.

## Repo layout

```
style/
├── source/           single source of truth
│   ├── rules/        always-on guidance
│   ├── skills/       on-demand expertise
│   └── commands/     slash-command prompts
├── scripts/          loader, lint, build, per-agent adapters
├── tests/            snapshot tests for adapters
├── docs/             newcomer-facing docs + ADRs
├── install.sh        thin wrapper around scripts/build.py
└── README.md
```

## Authoring

Add a new skill: drop a Markdown file under `source/skills/<id>.md` with the frontmatter shape shown in any existing skill. Run `python3 -m scripts.lint_source` to validate. Run `./install.sh --dry-run` to preview output.

Constraints:

- 200 lines max per source file.
- Every rule and skill has a `## GOOD` and a `## BAD` example section.
- Code examples primarily in Python; cross-language notes only when they sharpen the point.

## Requirements

- Python 3.10+.
- `pyyaml` (the installer will `pip install --user pyyaml` if it's missing).

## License

MIT.
