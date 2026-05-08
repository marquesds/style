#!/usr/bin/env bash
# style-harness installer — wraps scripts/build.py.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

python_bin="${PYTHON:-python3}"

if ! command -v "$python_bin" >/dev/null 2>&1; then
    echo "error: python3 not found; install Python 3.10+ and re-run." >&2
    exit 1
fi

if ! "$python_bin" -c 'import yaml' >/dev/null 2>&1; then
    echo "info: installing pyyaml --user (one-time)..."
    "$python_bin" -m pip install --user --quiet pyyaml
fi

exec "$python_bin" -m scripts.build "$@"
