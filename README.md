# Hoi4-Dev-Skills

> **Status: under active development.** First release will target HOI4 1.19.x.

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
  loop.
- **Honest claims.** Every hard claim in the skill is tied to a source
  (game dump, game file, or attributed wiki paraphrase) in
  `docs/claims-register.md`.

## Tools (available now)

```bash
pip install -r requirements-dev.txt   # dev only; the tools themselves are stdlib

python tools/extract.py               # game docs → version-stamped JSON (extracted/)
python tools/validate.py <mod_dir>    # static mod lint (braces, IDs, loc keys, overrides)
python tools/error_triage.py logs/error.log --against baseline.log
```

See [docs/setup-game-data.md](docs/setup-game-data.md).

## The skill (available now)

`skills/hoi4-modding/` is an [Agent Skills](https://agentskills.io)-compliant
skill for Claude Code, Codex, Cursor, Gemini CLI, OpenCode and other agents:

- **Router** (`SKILL.md`): core rules (scope flow, encoding, verification),
  evidence lanes (lint → log triage → game run), and a routing table.
- **References** (loaded on demand): [events](skills/hoi4-modding/references/events.md),
  [national focus trees](skills/hoi4-modding/references/national-focus.md),
  [mod structure](skills/hoi4-modding/references/mod-structure.md),
  [debugging and logs](skills/hoi4-modding/references/debugging-and-logs.md).
- **Asset kits**: copy-paste event and decision file sets that pass the
  validator out of the box.
- **Claims register**: [docs/claims-register.md](docs/claims-register.md) —
  every hard claim tied to game docs, game files, or observed logs.

Install by copying (or linking) `skills/hoi4-modding/` into your agent's
skills directory, e.g. `.claude/skills/` or `.agents/skills/` in your project.

## License

[MIT](LICENSE)
