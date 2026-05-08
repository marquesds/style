"""Build/install entrypoint.

Loads `source/`, runs lint, dispatches to per-agent adapters.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable
from pathlib import Path

from scripts.adapters import ADAPTERS, AdapterReport
from scripts.lint_source import lint_all
from scripts.source import ALLOWED_AGENTS, Source, SourceError, load_all

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "source"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="style-harness",
        description="Install style rules/skills/commands.",
    )
    p.add_argument(
        "--agent",
        choices=sorted(ALLOWED_AGENTS | {"all"}),
        default="all",
        help="target agent (default: all detected)",
    )
    p.add_argument(
        "--target-root",
        type=Path,
        default=Path(os.path.expanduser("~")),
        help="root dir under which agent config lives (default: $HOME)",
    )
    p.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE,
        help="directory containing rules/, skills/, commands/ (default: <repo>/source)",
    )
    p.add_argument("--dry-run", action="store_true", help="print operations, write nothing")
    p.add_argument("--no-lint", action="store_true", help="skip lint before install")
    return p.parse_args(argv)


def selected_agents(arg: str) -> list[str]:
    if arg == "all":
        return sorted(ALLOWED_AGENTS)
    return [arg]


def run(
    sources: Iterable[Source],
    target_root: Path,
    agents: Iterable[str],
    dry_run: bool,
) -> list[AdapterReport]:
    sources = list(sources)
    reports: list[AdapterReport] = []
    for name in agents:
        adapter = ADAPTERS[name]
        reports.append(adapter.write_all(sources, target_root=target_root, dry_run=dry_run))
    return reports


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        sources = load_all(args.source_dir)
    except SourceError as e:
        print(f"error loading sources: {e}", file=sys.stderr)
        return 2
    if not args.no_lint:
        errors = lint_all(sources)
        if errors:
            for err in errors:
                print(err, file=sys.stderr)
            msg = f"\nlint failed ({len(errors)} error(s)). Use --no-lint to skip."
            print(msg, file=sys.stderr)
            return 1
    reports = run(sources, args.target_root, selected_agents(args.agent), args.dry_run)
    for r in reports:
        r.print(prefix="dry-run: " if args.dry_run else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
