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
  [docs/claims-register.md](docs/claims-register.md) — 167 claims and
  counting.
- **MIT.** Free to fork, embed and build on (unlike CC-licensed
  alternatives).

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

Why plain CLIs instead of an MCP server: they run in any agent loop with
zero setup, and every one of them is covered by the test suite. A
read-only MCP wrapper can sit on top of these same binaries later.

## Contributing

Forks and PRs welcome — the core rule is simple: **every claim about game
behavior must be grounded** in the game's own docs, files, or logs. See
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

[MIT](LICENSE)
