#!/usr/bin/env bash
# Install the hoi4-modding skill into AI agent skill directories.
# One stored copy (this repo) is copied out to each agent; re-run to update.
#
# Usage:
#   ./install.sh                 # install into every detected agent
#   ./install.sh --agent claude  # only one agent (see AGENTS below)
#   ./install.sh --dest <dir>    # install into <dir>/hoi4-modding (manual)
#   ./install.sh --home <dir>    # override HOME (for tests / portable use)
#
# Verified on Git Bash (Windows) and Linux; macOS untested.

set -euo pipefail
cd "$(dirname "$0")"

SKILL_SRC="skills/hoi4-modding"
SKILL_NAME="hoi4-modding"

# agent name -> skills dir (relative to HOME)
AGENTS=(
  "claude:.claude/skills"
  "zcode:.agents/skills"
  "codex:.codex/skills"
  "cursor:.cursor/skills"
  "gemini:.gemini/skills"
  "opencode:.config/opencode/skills"
  "copilot:.copilot/skills"
)

HOME_OVERRIDE=""
DEST=""
WANT_AGENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --home) HOME_OVERRIDE="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    --agent) WANT_AGENT="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

install_to() {
  local target_dir="$1"
  local target="$target_dir/$SKILL_NAME"
  if [[ -d "$target" ]]; then
    echo "already installed: $target (updating)"
    rm -rf "$target"
  fi
  mkdir -p "$target_dir"
  cp -R "$SKILL_SRC" "$target"
  echo "installed: $target"
}

if [[ -n "$DEST" ]]; then
  install_to "$DEST"
  exit 0
fi

BASE="${HOME_OVERRIDE:-${HOME:?HOME not set and no --home given}}"
found=0
for entry in "${AGENTS[@]}"; do
  name="${entry%%:*}"
  dir="${entry#*:}"
  if [[ -n "$WANT_AGENT" && "$name" != "$WANT_AGENT" ]]; then
    continue
  fi
  # install for an agent if its config dir exists, or it was explicitly asked
  if [[ -d "$BASE/${dir%%/*}" || "$name" == "$WANT_AGENT" ]]; then
    install_to "$BASE/$dir"
    found=1
  fi
done

if [[ "$found" -eq 0 ]]; then
  echo "no supported agent directories found under $BASE (or the agent name is unknown)."
  echo "install manually:  ./install.sh --dest <dir>   or  --agent <name>"
  echo "agents known: ${AGENTS[*]%%:*}"
  exit 1
fi
