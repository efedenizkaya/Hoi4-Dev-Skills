# Changelog

## 0.12.0 — Three 1.14+ systems: BoP, raids, operations

- `references/balance-of-power.md`: bands, sides, static-modifier
  contracts, full effect/trigger surface (verified in extracted JSON).
- `references/raids.md`: category + type databases, icon fallback chain,
  entity resolution order — grounded in the game's own
  `common/raids/_documentation.md`.
- `references/operations.md`: operation fields and the FROM = target
  scope contract.
- Coverage map updated: three systems move to covered; remaining
  uncovered leaders are peace_conference (35 files) then buildings.
- Register 116 claims; 20 references.

## 0.11.0 — Census-driven: units reference + coverage map

- Census of all 94 `common/` systems vs reference coverage (the honest
  gap list, kept as a permanent document).
- `references/units-and-equipment.md`: the biggest uncovered system (296
  vanilla files) — sub_units / equipment types / templates layers,
  grounded in the game's own `units/equipment/_documentation.md` and
  vanilla infantry.txt.
- `docs/coverage.md`: the coverage map itself — contributors pick work
  from the ranked uncovered list (peace_conference, bop, raids next),
  users check before trusting.
- Register 105 claims; 18 references.

## 0.10.0 — Scripted GUI reference, loc coverage tool, focus kit

- `references/scripted-gui.md`: the largest content gap, grounded in the
  game's own `common/scripted_guis/_documentation.md` (context types,
  anchoring, effects/triggers/properties binding) plus a vanilla census.
- `scripts/loc_report.py`: per-language localisation coverage vs english —
  the game falls back silently, so missing translations are invisible.
  On the dogfood mod (5 languages): surfaced 213 missing German keys out
  of 2244. No competitor has this.
- `assets/kits/focus-kit/`: third kit (mutual exclusion + shared
  prerequisite), validator-clean — and the new sprite rule immediately
  caught a nonexistent sprite name in its first draft, then validated
  0/0 against the real game dir.
- SKILL routing updated for all three.

## 0.9.1 — Adopted patterns from Fostanico v1.8.0

Ideas only — no CC BY-SA text or data copied, everything re-implemented in
this repo's tested-tool idiom:

- `scripts/override_audit.py`: inventories every mod file that exactly
  shadows a vanilla file (the full-file-replace breakage vector). Exit 1
  when overrides exist, so agents/CI notice. (Their audit script idea,
  now tested and stdlib.)
- `references/version-migration.md`: the ordered patch-recovery run —
  extract → `version_diff` → override audit → claims re-verification →
  mod validation — using only tools that ship with the skill. (Their
  migration workflow, grounded in our toolchain.)
- Kits now ship `verification.json`: machine-readable record of what was
  verified, by which tool, and an explicit `not_established` list (their
  honesty pattern; CONTRIBUTING now requires it for new kits).
- README documents why plain CLIs instead of an MCP server.

Deliberately NOT adopted: GUI-shader references (niche, deferred to the
scripted-GUI reference), runtime-test consent gating (our
proportionate-verification + never-simulate rules already cover it).

## 0.9.0 — Silent-failure rules

Three validator rules targeting behaviors the game ignores WITHOUT an
error (calibrated on vanilla + a real 19k-line mod; zero false positives):

- `unknown-modifier-name`: keys inside idea/dynamic-modifier/MIO modifier
  blocks checked against the extracted modifiers database, with template
  matching (`<Ideology>_drift` → `communism_drift`). Weight-grammar blocks
  (ai_will_do/ai_chance/mtth, tree country factors) are excluded.
- `unknown-sprite`: icon/picture/background GFX references must be declared
  in some mod or vanilla .gfx (interface + dlc scanned). Found 18 real
  dangling sprites in the dogfood mod.
- `unknown-on-action`: mod on_action hooks must exist in the vanilla hook
  list — a misspelled hook never fires, silently.
- Wrapper CLIs (`python tools/*.py`) now forward to the skill
  implementations correctly (regression: wrappers ran but never invoked
  main).
- `docs/cwtools.md`: CWTools documented as the complementary deep
  validator, with maintenance status (action stale since 2023-03) and an
  optional CI recipe.

## 0.8.0 — Competitive gap pass: searcher, migration, adapters

Gap analysis against eightman999, postigodev and the Agensi/Fostanico
package — everything adopted is re-implemented in this repo's idiom
(tools with tests + verification built in), nothing copied:

- `scripts/find.py`: identifier indexer — events, focuses, ideas,
  decisions, categories, scripted effects/triggers, characters, across
  mod + vanilla. `find <pattern>`, `--duplicates`, `--json`, exit codes.
  (Replaces six "searcher" skills and Fostanico's identifier-tracing MCP
  tool with one tested CLI.)
- `scripts/version_diff.py`: patch migration — added/removed
  effects/triggers/modifiers between two extracted versions. Feeds the
  `game update` workflow.
- `tools/new_mod.py` now routed in the skill; `new_mod` listed alongside.
- `adapters/` (Cursor `.mdc`, Cline rules) + repo-root `AGENTS.md` and
  `CLAUDE.md`.
- `prompts/`: four task playbooks (event chain, focus branch, error-log
  debug, mod review) — each ends in a mandatory verification step.
- `evals/trigger-evals.json`: skill-trigger regression data.
- `SECURITY.md`: no network, no auto-download, no game assets, no
  prompt-injection acceptance.

## 0.7.0 — Third-audit pass: distribution, scaffolding, broken cases

From the third independent audit (three-project competitive review):

- **Tools now ship inside the skill** (`skills/hoi4-modding/scripts/`) —
  an installed skill can validate mods standalone. Repo-root `tools/`
  became thin compatibility wrappers (imports and CLI keep working).
- **`tools/new_mod.py` scaffold**: descriptor pair, folder tree, BOM'd
  localisation, an event file with `add_namespace` declared — output
  passes the validator out of the box (mutation-tested).
- **Broken-case regression suite** (`tests/fixtures/broken/`): five
  broken minis with expected validator output, plus one documented gap
  (decision placement is not caught yet) that fails loudly when a rule
  starts catching it.
- **`missing-add-namespace` validator rule** (vanilla census: 128/128
  event files declare it) and **`--json`** output for agent/CI reads.
- **SKILL.md working agreement**: first-use discovery, review-vs-modify
  authority boundary, finding classification (definite/probable/
  heuristic/intentional), proportionate verification, response template.
- New references: `symptoms.md` (symptom-first troubleshooting) and
  `control-flow.md` (if/limit, iteration families, random_list, event
  targets, loops) — grounded in the game's script docs and vanilla usage.
  LIOS/FIOS + alphabetical load order documented in mod-structure.md.
- Register honesty: `[unverified]` tags now appear in reference text at
  the 9 unverified claim sites (93 claims total).
- Audit items REJECTED with evidence: `common/static_modifiers/` folder
  does not exist (static modifiers live in `common/modifiers/`);
  `>=`/`<=` comparison operators are not used anywhere in vanilla
  common/ scripts (no rule added).

## 0.6.0 — Owner-audit fix pass

The owner ran an independent audit; every factual finding was re-verified
against the vanilla game files before acting. 11 of 12 P0 findings confirmed
and fixed; one REJECTED (HOI4 scripted effects have no `$ARG$` parameter
syntax — that is CK3/Stellaris; vanilla `common/scripted_effects/` contains
zero `$`).

Content corrections (all now vanilla-sourced in the claims register):
- Decision `cost` defaults to political power; command-power decisions use
  `custom_cost_trigger`/`custom_cost_text` (BEL.txt pattern).
- Focus `cost` is points (define `FOCUS_POINT_DAYS = 7` — one point is a
  week, not a day); tree selection uses `factor = 0` + per-tag modifiers.
- Loc icons are `£token` (never `@icon!`); dynamic values `$var$`;
  language folder is `simp_chinese`; scripted loc roots at `defined_text`.
- `change_variable` does not exist → `subtract_from_variable`; static
  modifiers live in `common/modifiers/` (modifier_definitions declares
  custom types); event files declare namespaces with `add_namespace`.
- Decision kit rewritten: decisions embedded in the category block
  (vanilla AFG.txt pattern); event kit declares `add_namespace`.

Tool fixes (audit P1):
- `duplicate-focus-id` rule added (the game silently keeps one copy).
- `focus-position-overlap` no longer fires for `relative_position_id`
  focuses (43 false positives removed on the real mod).
- Focus prerequisites are vanilla-aware when the game dir is provided.
- `error_triage --against` now exits 1 on net regressions (CI gate) and
  reports improvements on a clean current log instead of swallowing them;
  new classes: `parse-error`, `unknown-modifier`.
- Event duplicate-id scan is O(n) (was O(n²) per header) and covers
  `events/**` consistently with the statement-name check.

Honesty engineering (audit P2):
- Claims register marks `**unverified**` rows explicitly (11) with a
  reader-facing note; doubled CLAIM markers deduplicated.
- One rejected audit finding is documented here so it stays rejected.

## 0.5.2 — Portability and robustness

- `find_game_dir()` knows Linux (`~/.steam/steam`, `~/.local/share/Steam`)
  and macOS (`~/Library/Application Support/Steam`) library layouts, not
  just Windows — first existing candidate wins.
- Escaped quotes (`\"`) inside strings are string content, not closers —
  vanilla division strings contain nested `\"...\"`.
- `extract`/parser tolerate malformed bytes (`errors="replace"`) instead
  of aborting with a traceback.
- Statement scan uses a single running-depth pass (was O(body²) counting).
- CI: pip cache, concurrency group, read-only permissions.

## 0.5.1 — Audit fix pass

From the whole-project audit (fresh reviewer, 7 dimensions):

- `_EVENT_ID_RE` rewritten: header + balanced-body scan at depth 0, so
  `id =` after nested blocks is found and firing effects inside options
  stay excluded; `events/**` subdirectories now scanned for duplicates,
  loc refs and vanilla overrides.
- `--data` pointing nowhere exits 2 with a clear message; a bad explicit
  `--game-dir` warns on stderr instead of silently disabling checks.
- install.ps1 now smoke-tested (pytest + Windows CI leg); installer
  messages moved to stdout; idempotency pinned.
- Vacuous vanilla-focus test replaced with a real pin (fake_game focus
  tree; garbage ids still flagged).
- README claim count now derived from the register by a test (cannot
  drift); register 72 → 81 rows; 8 previously unmarked behavioral claims
  in references now carry CLAIM markers.
- national-focus.md no longer overstates validator focus-id coverage;
  garbled `text_icon` sentence fixed; SKILL.md claims-register link and
  tool-availability wording corrected for installed copies.

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
