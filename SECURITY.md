# Security Policy

This project ships **instructions + local Python scripts**. It has no
network access, no telemetry, and no execution surface beyond the tools
documented in this repository.

The tooling will not:

- execute subprocesses or shell commands, and makes no network calls
  (the CLI tools are stdlib-only; the optional MCP server talks over
  stdio only)
- download external files automatically
- copy proprietary HOI4 or DLC assets into this repository (game-derived
  data is extracted on the user's machine and git-ignored)
- ask agents to ignore user, system, or platform safety instructions
- hide instructions in metadata, adapters, or fixture files

## Write behavior

Tools read any path you point them at. They write only where you tell
them to on the command line, and each writer has a narrow, documented
target:

- `loc_sync.py` — creates `zz_sync_l_<lang>.yml` stub files inside the
  target mod's `localisation/<lang>/` folder. It never edits existing
  files; a re-run overwrites only its own previously generated stub.
- `extract.py` — writes version-stamped JSON into the output directory
  you pass (`--out`, default `extracted/` in the current directory).
- `new_mod.py` — creates a new mod directory plus a `.mod` sidecar under
  the parent directory you pass (`--dir`, default `.`). It refuses to
  run if either already exists, so it never overwrites.
- Report writers — `doctor.py --out`, `balance_lab.py --out`,
  `focus_map.py --html`, `playtest.py --results`, and `architect.py`
  (`--project`, which later subcommands keep updating, plus `check
  --out`) — write exactly the file path you pass.

User-chosen output paths are written as given: pointing a report writer
at an existing file will overwrite that file. The MCP server
(mcp-server/) is strictly read-only — it never writes and never
launches the game.

Contributions are rejected if they add instructions to bypass user,
system, platform, repository, or safety constraints, or if they hide
instructions in metadata or adapter files.

## Reporting

Report vulnerabilities or prompt-injection concerns via GitHub
[private vulnerability reporting](https://github.com/efedenizkaya/Hoi4-Dev-Skills/security/advisories/new),
or open a normal issue for non-sensitive policy questions.

## Data handling

Reference data is extracted from the user's own game install
(`extracted/`, git-ignored) and never committed. The only game-derived
data that may be committed is the sanitized counts-only
`docs/data-summaries/*.json`.
