# Contributing

## The one rule that makes this project valuable

**Every hard claim is grounded.** If you add or change a statement about
game behavior (a field name, a limit, a "this does X"), it carries a
`CLAIM(<id>)` marker in the reference and a row in
[claims-register.md](claims-register.md) citing a source:

- `game-doc` — a file in `<game>/documentation/` (best: machine-generated,
  version-stamped)
- `game-file` — a vanilla file you inspected (name the file)
- `log` — a line you observed in the game's own logs
- `tool` — this repo's tooling (tests count)

"Someone on a forum said so" is not a source. If a claim cannot be
grounded yet, mark the row honestly (`verify on use`) instead of dropping
the marker.

## Development setup

```bash
git clone https://github.com/efedenizkaya/Hoi4-Dev-Skills.git
cd Hoi4-Dev-Skills
pip install pytest
python -m pytest            # full suite; installs must stay green
```

Structure:

```
skills/hoi4-modding/   # the skill (router + references + kits) — docs, keep < limits
tools/                 # stdlib Python CLIs (extract, validate, triage) — TDD
tests/                 # pytest; fixtures are synthetic, never game files
docs/                  # setup, claims register, tutorial
```

House rules:

- Tools: Python 3.10+ **stdlib only** at runtime; pytest is dev-only.
- Tests first for any code change (the suite is the review gate).
- Reference files stay under ~400 lines; SKILL.md under 500 (enforced).
- Nothing game-derived or user-identifying is ever committed
  (`extracted/` is git-ignored; use `%USERPROFILE%` in examples).
- One reference per domain; prefer editing the existing file over new
  files unless the domain is genuinely new.
- New asset kits must ship a `verification.json` (what was verified,
  with which tool, and an explicit `not_established` list).

## Fork and pull request flow

1. **Fork** the repo on GitHub, then:

   ```bash
   git clone https://github.com/<you>/Hoi4-Dev-Skills.git
   cd Hoi4-Dev-Skills
   git checkout -b my-change
   ```

2. Make the change with tests. For reference edits, update
   `docs/claims-register.md` rows for any claim you touched (re-verify
   against your own game install — `python tools/extract.py`).
3. Run the suite; every test green including the skill lint.
4. Push to your fork and open a **pull request** against `main`.
   Describe: what changed, which claims were (re)verified and against
   which game version.

CI runs the suite on Linux and Windows plus the install smoke test and
frontmatter validation. A red CI means the PR waits.

## Reporting game-version drift

A new HOI4 patch invalidates the version stamp. Open an issue titled
`game update <version>` with:

```bash
python tools/extract.py --summary-out summary.json   # attach summary.json
python tools/validate.py <a_mod_you_have>            # paste the tail
```

The summary is counts-only (safe to share). Maintainers re-verify the
claims register rows marked with the old version.
