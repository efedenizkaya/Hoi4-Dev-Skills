# Installation

## What you get

- **The skill** — `skills/hoi4-modding/`: knowledge for your AI agent
  (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Copilot, ZCode…).
- **The tools** — `tools/`: the verification loop the skill instructs the
  agent to use (`extract.py`, `validate.py`, `error_triage.py`). They run
  from this repository checkout with Python 3.10+, no dependencies.

## Option A: install the skill (per machine)

Windows (PowerShell):

```powershell
git clone https://github.com/efedenizkaya/Hoi4-Dev-Skills.git
cd Hoi4-Dev-Skills
powershell -ExecutionPolicy Bypass -File install.ps1
```

Linux / macOS / Git Bash:

```bash
git clone https://github.com/efedenizkaya/Hoi4-Dev-Skills.git
cd Hoi4-Dev-Skills
./install.sh
```

The script copies `skills/hoi4-modding/` into every agent skills directory
it finds under your home dir (`.claude/skills`, `.agents/skills`,
`.codex/skills`, `.cursor/skills`, `.gemini/skills`,
`.config/opencode/skills`, `.copilot/skills`). Re-run it after `git pull`
to update. Target one agent with `--agent claude`, or anywhere with
`--dest <dir>`.

Status tiers:

| Tier | Agents | Meaning |
|---|---|---|
| Verified | ZCode, Claude Code | installed and exercised daily by the maintainer |
| Best effort | Codex, Cursor, Gemini CLI, OpenCode, Copilot | spec-compliant install, not manually verified |

Platform notes (researched 2026-10-31):
- **Codex** also scans the industry-standard `~/.agents/skills` (the
  `zcode` entry installs there), but some Codex versions skip
  `~/.codex/skills` — if skills don't appear, symlink it to
  `~/.agents/skills`.
- **Copilot**: repo-level skills live in `.github/skills/` (copy the
  skill there per-project); `~/.copilot/skills` is the cross-project
  location this installer uses. Copilot also reads `.claude/skills` and
  `.agents/skills` natively.

## Option B: install into one project

Copy (or link) the skill into the project so teammates get it via git:

```bash
mkdir -p .agents/skills
cp -R /path/to/Hoi4-Dev-Skills/skills/hoi4-modding .agents/skills/
```

Commit it — the skill is data, not code that could diverge.

## Codex / one-line install

Codex (and any shell-capable agent) can install everything itself:

```bash
git clone https://github.com/efedenizkaya/Hoi4-Dev-Skills.git &&
  cd Hoi4-Dev-Skills && ./install.sh --agent codex
```

## Templates for your mod repository

`templates/` holds `mod-AGENTS.md` and `mod-CLAUDE.md` — copy the one
matching your agent into your mod repository so the agent that opens it
knows the verification rules (validate after every change, review ≠
modify, sourced claims).

## Set up the verification tools

The skill tells your agent to run the tools; make them reachable:

```bash
# from the repo checkout
python tools/extract.py        # reads YOUR game install, writes extracted/
python tools/validate.py <your_mod>     # quick check it works
```

If auto-detection of the Steam install fails, set `HOI4_GAME_DIR`. Details:
[setup-game-data.md](setup-game-data.md).

Nothing game-derived leaves your machine; `extracted/` is git-ignored.

## Verify the install

Ask your agent: *"What does the hoi4-modding skill say about mutually
exclusive focuses?"* — it should cite the reference and the claims
register, not answer purely from memory. Or run the repo test suite:

```bash
pip install pytest && python -m pytest
```
