#!/usr/bin/env bash
# Runs the full correctness suite. No GPU required.
set -euo pipefail
# Use the local venv when there is one, otherwise whatever python is on PATH,
# so the suite runs unchanged on a cloud box that has no venv.
PY=${PYTHON:-$([ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)}
fail=0
for f in tests/test_*.py; do
  echo "--- $f"
  "$PY" "$f" || fail=1
done
[ $fail -eq 0 ] && echo "ALL TESTS PASS" || { echo "FAILURES"; exit 1; }
