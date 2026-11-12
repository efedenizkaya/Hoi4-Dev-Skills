# Hoi4-Dev-Skills

[![CI](https://github.com/efedenizkaya/Hoi4-Dev-Skills/actions/workflows/ci.yml/badge.svg)](https://github.com/efedenizkaya/Hoi4-Dev-Skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Status: usable.** Skill + tools verified against HOI4 **1.19.4.1**
> ("Operation Postern"). See the [changelog](CHANGELOG.md).

Verified, game-derived Agent Skill and tooling for AI-assisted
**Hearts of Iron IV** modding. Makes AI coding assistants (Claude Code,
Codex, Cursor, Gemini CLI, OpenCode, ZCode, …) write mod code that the
game itself accepts — checked against the game's own error logs and the
official documentation shipped inside the game install.

## How it is different

- **Engine-derived, not wiki-scraped.** Reference data is extracted from
  the game's own version-stamped documentation files on the player's
  machine — always current for the installed patch. Nothing
  game-derived is committed to this repo.
- **Verification built in.** A static mod validator, an `error.log`
  triage tool, and a documented "launch with `-debug`, diff the errors"
  loop. The skill refuses to claim a mod works without evidence.
- **Honest claims.** Every hard claim in the skill is tied to a source
  (game docs, game file, or observed log) in
  [docs/claims-register.md](docs/claims-register.md) — 186 claims and
  counting.
- **MIT.** Free to fork, embed and build on (unlike CC-licensed
  alternatives).
- **Battle-tested on a real mod.** See the failure census in
  [docs/dogfood-lessons.md](docs/dogfood-lessons.md) — 833 duplicate
  loc keys, 34 dangling event targets and 18 phantom sprites found in
  one actively-played hand-made mod.

[Türkçe README](README_tr.md)

## Quick start

```bash
git clone https://github.com/efedenizkaya/Hoi4-Dev-Skills.git
cd Hoi4-Dev-Skills
./install.sh                                   # or install.ps1 on Windows
python tools/extract.py                        # reads YOUR game install
python tools/validate.py <mod_dir>             # static mod lint
python tools/error_triage.py logs/error.log --against baseline.log
```

Full walkthrough: [docs/tutorial.md](docs/tutorial.md) — from zero to a
verified event in ~15 minutes.

### First things to try

Paste any of these to an agent with the skill installed:

- *"Run the doctor on my mod at `<path>` and give me the top 5 findings."*
- *"Add a decision that gives 5% stability for 50 political power to my
  mod at `<path>` — then prove it validates."*
- *"Where is `GER_four_year_plan` defined, and what references it?"*
- *"My event shows raw text like `myevent.1.t` — find out why."*
- *"We just got patch 1.20 — diff the extracted data and tell me what
  broke."*

## The skill

`skills/hoi4-modding/` is an [Agent Skills](https://agentskills.io)-compliant
skill:

- **Router** (`SKILL.md`): core rules (scope flow, encoding, verification),
  evidence lanes (lint → log triage → game run), and a routing table.
- **27 references** (loaded on demand): every `common/` system from AI
  strategy and characters through peace conferences, special projects and
  map orientation — full map in [docs/coverage.md](docs/coverage.md).
- **Asset kits**: copy-paste event and decision file sets that pass the
  validator out of the box.
- **Claims register**: every hard claim sourced and version-stamped.

Install details and agent support tiers:
[docs/INSTALLATION.md](docs/INSTALLATION.md).

## The tools

| Tool | Job |
|---|---|
| `tools/extract.py` | game's machine-generated docs → version-stamped JSON (`extracted/<version>/`, git-ignored) |
| `tools/validate.py` | static lint: braces/quotes, duplicate event ids, missing loc keys, focus-tree rules (prerequisites, bidirectional exclusivity, grid overlap), vanilla override awareness, and — with `--data` — effect/trigger name checks against the extracted database |
| `tools/error_triage.py` | parse, classify and diff `error.log` between two runs — only deltas matter |

Python 3.10+, stdlib only — CI exercises it on the maintainer's
self-hosted Windows runner (Python 3.14) via `ci.yml`; other platforms
and versions are untested. Details:
[docs/setup-game-data.md](docs/setup-game-data.md).

An optional read-only MCP server over these same tools now exists —
see [docs/MCP.md](docs/MCP.md). The CLIs remain the primary interface
(zero setup, every agent).

## Asset and legal posture

- This repository contains **only** original text, tested Python tooling
  and synthetic fixtures. No HOI4 game files, DLC assets, workshop mods,
  wiki text or CC BY-SA content from other projects is committed — ever.
- Reference data is extracted **on the user's own machine** from their
  own game install (`extracted/`, git-ignored). Nothing game-derived
  leaves that machine through this project.
- The only game-derived data in the repo is counts-only metadata
  (`docs/data-summaries/*.json`: version + how many effects/triggers
  exist) — facts about numbers, not content.
- Ideas adopted from competitor projects are re-implemented from scratch
  in this repo's idiom; no text, code or data is copied.
- Steam Workshop content found on disk is used only as local read-only
  reference during development and never redistributed.

## Contributing

Forks and PRs welcome — the core rule is simple: **every claim about game
behavior must be grounded** in the game's own docs, files, or logs. See
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

[MIT](LICENSE)
