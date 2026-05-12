# style

A language-agnostic, single-source-of-truth coding-style harness that feeds my
practices into any AI coding agent.

## Install

```bash
git clone https://github.com/<you>/style ~/.style
cd ~/.style
./install.sh                   # installs into all detected agents
./install.sh --agent claude    # only one agent
./install.sh --dry-run         # show what would change, write nothing
```

The installer writes only into a managed namespace inside each agent's config
directory and never clobbers files outside it. Re-running is idempotent.

## Uninstall

```bash
./uninstall.sh                 # remove harness from every detected agent
./uninstall.sh --agent cursor  # only one agent
./uninstall.sh --dry-run       # show what would be removed, write nothing
```

The uninstaller deletes only files carrying the `<!-- style-harness:managed -->` marker
and strips the `<!-- BEGIN style-harness --> … <!-- END style-harness -->` block from
merged config files. User-authored content is never touched.

## What gets installed

| Bucket | What it is |
|--------|-----------|
| Rules (`source/rules/`) | Always-on guidance: workflow, code quality, design principles, observability, skills catalog |
| Skills (`source/skills/`) | On-demand expertise loaded from the skills catalog: TDD, bug-first, hexagonal, REST, UoW, code review, and more |
| Commands (`source/commands/`) | Slash-command prompts: `/spec`, `/plan`, `/tdd`, `/bug`, `/review`, `/done`, `/commit` |

For the philosophy behind what is installed, see `docs/style-overview.md`.

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
├── AGENTS.md         contributor rules for AI agents working on this repo
└── README.md
```

## Authoring

See `docs/contributing.md` and `AGENTS.md`.

## Requirements

- Python 3.10+.
- `pyyaml` (the installer will `pip install --user pyyaml` if it's missing).

## License

MIT.
