#!/usr/bin/env bash
# Install the hoi4-modding skill into AI agent skill directories.
# One stored copy (this repo) is copied out to each agent; re-run to update.
#
# Usage:
#   ./install.sh                 # install into every detected agent
#   ./install.sh --agent claude  # only one agent (see AGENTS below)
#   ./install.sh --dest <dir>    # install into <dir>/hoi4-modding (manual)
#   ./install.sh --home <dir>    # override HOME (for tests / portable use)
#   ./install.sh --list          # show known agents and install state
#   ./install.sh --dry-run       # show what would happen, touch nothing
#   ./install.sh --update        # refresh already-installed copies only
#   ./install.sh --uninstall     # remove the skill dirs this tool created
#
# Verified on Git Bash (Windows) and Linux; macOS untested.

set -euo pipefail
cd "$(dirname "$0")"

SKILL_SRC="skills/hoi4-modding"
SKILL_NAME="hoi4-modding"

# agent name -> skills dir (relative to HOME)
# NOTE (researched 2026-10-31):
#  - Codex also scans ~/.agents/skills (industry standard) but some
#    versions skip ~/.codex/skills — the zcode entry installs there too.
#  - Copilot's repo-level location is .github/skills/ (see INSTALLATION.md);
#    the personal entry below is correct for cross-project use.
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
MODE="install"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --home) HOME_OVERRIDE="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    --agent) WANT_AGENT="$2"; shift 2 ;;
    --list) MODE="list"; shift ;;
    --dry-run) MODE="dry-run"; shift ;;
    --update) MODE="update"; shift ;;
    --uninstall) MODE="uninstall"; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

install_to() {
  local target_dir="$1"
  local target="$target_dir/$SKILL_NAME"
  if [[ "$MODE" == "dry-run" ]]; then
    if [[ -d "$target" ]]; then
      echo "would update: $target"
    else
      echo "would install: $target"
    fi
    return
  fi
  if [[ "$MODE" == "update" && ! -d "$target" ]]; then
    return   # update touches only already-installed copies
  fi
  if [[ -d "$target" ]]; then
    echo "already installed: $target (updating)"
    rm -rf "$target"
  fi
  mkdir -p "$target_dir"
  cp -R "$SKILL_SRC" "$target"
  echo "installed: $target"
}

list_agents() {
  local base="${1:-${HOME:?}}"
  for entry in "${AGENTS[@]}"; do
    name="${entry%%:*}"; dir="${entry#*:}"
    state="not installed"
    [[ -d "$base/$dir/$SKILL_NAME" ]] && state="installed"
    printf '%-10s %-30s %s
' "$name" "$base/$dir" "$state"
  done
}

uninstall_all() {
  local base="${1:?}"
  local removed=0
  for entry in "${AGENTS[@]}"; do
    dir="${entry#*:}"
    local target="$base/$dir/$SKILL_NAME"
    if [[ -d "$target" ]]; then
      rm -rf "$target"
      echo "removed: $target"
      removed=1
    fi
  done
  [[ "$removed" -eq 1 ]] || echo "nothing to uninstall under $base"
}

if [[ "$MODE" == "list" ]]; then
  list_agents "${HOME_OVERRIDE:-${HOME:-}}"
  exit 0
fi
if [[ "$MODE" == "uninstall" ]]; then
  uninstall_all "${HOME_OVERRIDE:-${HOME:?HOME not set and no --home given}}"
  exit 0
fi

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
