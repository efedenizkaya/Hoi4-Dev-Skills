#!/usr/bin/env bash
# Smoke test for install.sh — run with a temp HOME.
# Invoked by pytest (tests/test_install.py) and CI.
set -euo pipefail
cd "$(dirname "$0")/.."

TMP=$(mktemp -d)
TMP2=$(mktemp -d)
trap 'rm -rf "$TMP" "$TMP2"' EXIT

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

# ---- installer v2 flags ----
LIST=$(bash install.sh --home "$TMP" --list)
echo "$LIST" | grep -q "claude" && echo "$LIST" | grep -q "zcode"

# dry-run must not touch the filesystem
bash install.sh --home "$TMP2" --agent gemini --dry-run >/dev/null
test ! -d "$TMP2" && echo "dry-run clean"

# update = install over existing (idempotent, refreshes content)
echo "STALE" >> "$TMP/.claude/skills/hoi4-modding/SKILL.md"
bash install.sh --home "$TMP" --agent claude >/dev/null
grep -q "STALE" "$TMP/.claude/skills/hoi4-modding/SKILL.md" && exit 1 || true
grep -q "HOI4 Modding Skill" "$TMP/.claude/skills/hoi4-modding/SKILL.md"

# uninstall removes only the skill dir it owns, leaves the agent dir
bash install.sh --home "$TMP" --agent claude --uninstall >/dev/null
test ! -d "$TMP/.claude/skills/hoi4-modding"
test -d "$TMP/.claude/skills"
echo "installer v2 smoke OK"
