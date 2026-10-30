# Changelog

## 0.5.0 — Data-aware validation

- `validate.py --data <extracted_dir>`: statement names in effect contexts
  checked against the extracted effect/trigger databases (warnings-only,
  depth-1 scan to respect effect argument schemas).
- `has_completed_focus` targets checked against mod + vanilla focus trees
  (game-dir aware). Vanilla scripted effect names count as known.
- Calibration on a real 19k-line mod: naive scan 11,541 false positives →
  134 meaningful warnings after depth-1 + vanilla-name fixes; found real
  dangling scripted-effect calls.
- New guard: splice bug fixed where cut sub-blocks left stray braces that
  corrupted depth counting.

## 0.4.1 — Focus-tree rules, repo polish

- Validator v2 focus rules (grounded in the claims register):
  `missing-focus-prerequisite` (error), `unidirectional-mutual-exclusive`
  (warning — vanilla declares both sides), `focus-position-overlap`
  (warning). Focus line numbers verified against a real 9-file tree.
- GitHub: repo description + topics set; PR template with claim-
  verification table; `game update` issue form for patch-drift reports.
- Note: CI failures on 2026-10-30 were account billing (jobs never
  started), not test failures.

## 0.4.0 — Install, CI, tutorial

- `install.sh` / `install.ps1` / `install.cmd`: multi-agent skill install
  with detection, `--agent`, `--dest`, `--home` overrides; POSIX smoke
  test in the suite.
- CI: pytest on Linux + Windows, install smoke, skills-ref frontmatter
  validation.
- Docs: INSTALLATION.md, CONTRIBUTING.md (fork/PR + claim-grounding
  rules), docs/tutorial.md (zero → verified event).
- Validator: fixed false duplicate-event-id when a firing
  `country_event` effect appears inside an option (brace-depth check).

## 0.3.0 — Full reference coverage

- 10 new references: ideas & modifiers, decisions, characters, MIO,
  variables & scripting, localisation, gfx & assets, AI strategy, tech
  tree, map/states/history — all grounded in the game's own docs and
  vanilla files.
- Claims register: 22 → 71 sourced claims.
- New guard test: every reference must appear in the SKILL.md routing
  table.
- Validator: fixed quote-masking false positives (unbalanced-quotes);
  duplicate-event-id now reports the id line, not the block start.

## 0.2.0 — Skill core

- `skills/hoi4-modding/`: Agent-Skills-compliant router (core rules,
  evidence lanes, verification loop, routing table).
- 4 references (events, national-focus, mod-structure,
  debugging-and-logs), claims register seeded, event & decision kits.
- Validator gained base-game awareness (vanilla loc keys accepted,
  vanilla event re-definition downgraded to warning).

## 0.1.0 — Tools

- `tools/pdx_doc_parser.py`: parser for the game's machine-generated
  `documentation/*.md`.
- `tools/extract.py`: version-stamped JSON extraction from the local
  game install.
- `tools/validate.py`: static mod lint (braces/quotes, duplicate ids,
  missing loc keys).
- `tools/error_triage.py`: error.log parse, classify, diff.
- Dogfooded against HOI4 1.19.4.1 and a real hand-made mod.
