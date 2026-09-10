#!/usr/bin/env bash
# Everything this repo checks before a change goes out: byte-compile every
# script, syntax-check every shell script, run the unit tests. No dependencies,
# no network, no binaries needed - safe to run anywhere.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

echo "== python syntax =="
python3 -m py_compile scripts/*.py tests/*.py

echo "== shell syntax =="
bash -n scripts/*.sh

echo "== unit tests =="
python3 -m unittest discover -s tests "$@"

echo "all checks passed"
