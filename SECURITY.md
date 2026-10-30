# Security Policy

This project ships **instructions + local Python scripts**. It has no
network access, no telemetry, and no execution surface beyond the tools
documented in this repository.

The tooling will not:

- execute shell commands beyond the documented validator/extractor/triage
  invocations
- download external files automatically
- modify files outside the mod directory the user points it at
- copy proprietary HOI4 or DLC assets into this repository (game-derived
  data is extracted on the user's machine and git-ignored)
- ask agents to ignore user, system, or platform safety instructions
- hide instructions in metadata, adapters, or fixture files

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
