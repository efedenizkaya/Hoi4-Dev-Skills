#!/usr/bin/env bash
# Smoke test for install.sh — run with a temp HOME.
# Invoked by pytest (tests/test_install.py) and CI.
set -euo pipefail
cd "$(dirname "$0")/.."

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

bash install.sh --home "$TMP" --agent claude >/dev/null
test -f "$TMP/.claude/skills/hoi4-modding/SKILL.md"
test -f "$TMP/.claude/skills/hoi4-modding/references/events.md"

# --dest installs wherever told, no agent detection needed
bash install.sh --dest "$TMP/anywhere" >/dev/null
test -f "$TMP/anywhere/hoi4-modding/SKILL.md"

# idempotent: second run succeeds and reports already installed
out=$(bash install.sh --home "$TMP" --agent claude)
echo "$out" | grep -q "already installed"

echo "install.sh smoke test OK"
