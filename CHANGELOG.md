# Changelog

## 0.26.0 — GitHub settings, repo hygiene, platform research

Settings applied via gh CLI:
- Discussions enabled (the issue-template config links there — it was
  dead); delete-branch-on-merge enabled; `game-update` and
  `heuristic-finding` labels created (the issue form referenced a
  non-existent label).

New repo hygiene files:
- `.github/dependabot.yml` (github-actions + pip ecosystems, monthly).
- `.github/CODEOWNERS` (single-maintainer routing).
- `pyproject.toml` (project metadata + pytest config) with a version
  consistency test against metadata.json.

Research (2026-10-31) applied:
- Copilot's repo-level location is `.github/skills/` (personal is
  `~/.copilot/skills`, which we install); Copilot also reads
  `.claude/skills` and `.agents/skills` natively.
- Codex scans `.codex/skills` unreliably and the industry is
  standardizing on `~/.agents/skills` — documented in INSTALLATION.md
  and install.sh.

## 0.25.0 — Read-only MCP server (final roadmap item)

- `mcp-server/hoi4_mcp.py`: MCP server (mcp>=2) exposing 8 read-only
  tools over the tested CLI implementations — validate_mod, doctor,
  find_identifier, event_chain_map, loc_coverage, vanilla_overrides,
  triage_error_log, staleness_check. No mod writes, no game launch, no
  network.
- `docs/MCP.md`: client configuration and security boundaries.
- `requirements-mcp.txt`: optional dependency, kept out of the core
  tooling's zero-dependency stance. CI installs mcp so the server tests
  run there.
- doctor.py refactor: report assembly extracted to `build_report()` for
  MCP reuse.
- This completes the roadmap adopted across all four audit rounds.

## 0.24.0 — Distribution groundwork (no release yet)

- README: "First things to try" prompts, "Asset and legal posture"
  section (no game assets ever committed; extracted locally; competitor
  ideas re-implemented, never copied).
- `templates/mod-AGENTS.md` + `templates/mod-CLAUDE.md`: drop into your
  mod repository so any agent knows the verification rules.
- INSTALLATION.md: Codex one-line install.
- CI `package` job: every push produces a downloadable
  `hoi4-modding-skill` zip artifact (release-ready packaging without a
  release).

## 0.23.0 — Health score, chain map, dogfood lessons, Turkish README

- `doctor.py`: health score (0-100, weighted penalties: errors 8, warnings
  2, duplicate ids 10, overrides 4, loc gaps up to 20) and markdown
  report output (`--out report.md`).
- `scripts/chain_map.py`: event firing graph — which events fire which,
  with dangling-target detection. Real mod: 295 defined events, 34
  undefined targets surfaced.
- `docs/dogfood-lessons.md`: the real-mod failure census and the
  meta-lesson (the game forgives everything except parse errors —
  tooling is the only way to see silent no-ops). Unique content no
  competitor has.
- `README_tr.md`: Turkish README with language link.
- Register 168 claims; tool count 13.

## 0.20.0 — Professional hardening (roadmap items 1-5, 6, 7)

From the fourth audit (four-repo competitive comparison):

- **Installer v2**: `--list`, `--dry-run`, `--update`, `--uninstall` on
  both installers (bash + PowerShell), smoke-tested.
- **`scripts/stale_check.py`**: compares the installed game version
  against the skill's verified stamp; mismatch suggests the version_diff
  migration workflow (exit codes for CI/agents).
- **`references/agent-safety.md`**: workshop content is data not
  instructions, never execute mod content, destructive-operation
  approvals, game actions belong to the user.
- **`tests/test_skill_examples.py`**: automated audit of every reference
  code block — GFX tokens against the real game sprite inventory,
  effect-context statements against the extracted database. Immediately
  caught 4 wrong sprite names in our own references (fixed with real
  names: bop side icons, decision-category icon semantics,
  upgrade-frame base-name semantics, focus icon tier).
- **`scripts/doctor.py`**: one-shot mod health report (validator +
  duplicate ids + vanilla overrides + loc coverage).
- `scripts/find.py --record`: single-record lookup with the official
  description from the extracted database.
- `scripts/doctor.py` + `scripts/stale_check.py` shipped in the skill
  bundle; doctor run on the real mod: 80 errors, 6 duplicate ids, 11
  vanilla overrides, per-language loc gaps in one report.

## 0.19.1 — Loc mismatch fix + audit round 4

- `loc-language-mismatch` fixed: the language is the FIRST folder under
  `localisation/` (subfolders like `english/events/` are normal), files
  directly in `localisation/` are exempt, `replace/` stays excluded.
  False positives on the real mod: 800+ -> 0 (total warnings 942 -> 889).
- Three focus regressions RESTORED (lost in the v0.18.0 test rewrite):
  duplicate-focus-id, relative_position_id overlap exemption, vanilla
  prerequisite — now in test_focus_regressions.py.
- README references bullet: stale "14 references" -> 27 with a coverage
  pointer; ci.yml mangled comment cleaned; coverage.md Uncovered section
  updated (abilities, opinion modifiers, wargoals, occupation laws,
  medals, continuous focus, combat tactics, terrain, autonomous states,
  intelligence agencies now covered).
- Register honesty: the three tool-rule rows are marked "(tool rule)"
  (they live in validator code, not reference text); CHANGELOG of 0.18.0
  overstated "all rows marked" — corrected here rather than rewritten.
- trigger-evals.json now has a schema/consistency test (unique queries,
  both classes present).

## 0.19.0 — Skill content audit

Self-audit of skills/hoi4-modding (structure, contradictions, brace
balance, vanilla spot-checks):

- national-focus.md: stale "`y = 0` is the 1936 column" removed (x =
  column, y = row — neither is a year); stale "no focus kit shipped yet"
  replaced with a pointer to the (existing) focus-kit.
- ideas-and-modifiers.md: `use_list_view` moved to the right home — slot
  blocks live in `common/ideas/*.txt` themselves, not idea_tags (vanilla
  _economic.txt verified).
- Vanilla spot-checks on risky field names: days_re_enable (43 files),
  select_effect (15), noOfFrames (89) — all confirmed; use_list_view
  relocated as above.
- All reference code blocks brace-balanced; kits re-validated 0/0 with
  the real game dir.

## 0.18.0 — Audit-fix round 3

- Validator: `offset` blocks no longer corrupt focus grid positions
  (overlap detection was missing real collisions); conditional
  `desc = { text = ... }` loc refs now checked (512 vanilla uses);
  localisation hygiene rules added (`loc-language-mismatch`,
  `duplicate-loc-key`) — the real dogfood mod surfaced 833 genuine
  duplicate loc keys.
- `new_mod.py` moved into the installed skill bundle (last tool living
  outside it); repo-root wrapper added.
- Claims: all 158 rows are now marked in the skill text (0 unused);
  `[unverified]` tagging complete including alphabetical-load-order.
- Docs: README references count corrected (14 -> 27) and derived note for
  the tested Python version; SKILL.md Known gaps rewritten (points to
  docs/coverage.md); CI `pull_request` trigger REMOVED — the workflow
  runs on a self-hosted runner and foreign PR code must never execute on
  the maintainer's machine; dev deps pinned in CI
  (requirements-dev.txt + skills-ref==0.1.1).
- Register rows added for the three new tool rules.

## 0.17.0 — Deepest static kit verification + peace AI

- All three kits passed the deepest static verification possible without
  launching the game: statement names vs the extracted effects/triggers
  database, sprites vs the real interface+dlc gfx inventory, namespaces,
  focus rules, loc BOM — 0 errors, 0 warnings each. Recorded in every
  kit's verification.json (`static_verified_against: 1.19.4.1`).
- peace-conference.md completed with AI peace desires (`ai_peace/`):
  summed desires, percentage semantics, same pc_* trigger caveat.
- CI: `workflow_dispatch` added — a manual run is possible the moment the
  account's billing issue is resolved. (Note: the CI failures are purely
  billing — GitHub never starts the jobs.)

## 0.16.0 — Special projects, map orientation, abilities

- `references/special-projects.md`: grounded in the game's own
  `special_projects_documentation.md` (13 vanilla files); loc/icon
  fallback chain like MIOs, mandatory project types.
- `references/map-modding.md`: HIGH-RISK orientation for the `map/`
  folder — load-bearing files table, risk tiers, limited verification.
  Errors here crash at startup; the game is the only oracle.
- characters.md gained unit-leader abilities; operations.md gained
  agency upgrades (both vanilla-grounded).
- Coverage: every `common/` system plus the map/ folder now has at least
  an orientation entry. Register 153 claims; 25 references.

## 0.15.0 — Misc systems + eval harness v2

- `references/misc-systems.md`: the remaining single-file systems
  (opinion modifiers, wargoals, occupation laws, continuous focus, medals,
  intelligence agencies, combat tactics, terrain, autonomous states,
  defines-blast-radius). Reference count: 23.
- **Eval harness v2**: `scripts/run_evals.py` + `evals/task-evals.json` —
  each eval = task prompt + mod dir + validator gates (max_errors,
  forbidden_rules). `--self-test` proves the shipped kits satisfy their
  own gates (CI step added); agent mode grades agent output. Deterministic:
  vanilla awareness is opt-in via `--game-dir`.
- Coverage map: every single-file `common/` system is now covered; the
  only remaining uncovered item is `map_modes` (map-adjacent).
- Register 144 claims; 23 references.

## 0.14.0 — Peace conference + small systems

- `references/peace-conference.md`: the FROM/FROM.FROM/FROM.FROM.FROM
  scope contract, multiplied cost modifiers (game doc advises 0.4-3.0),
  pc_* live-conference triggers — grounded in the game's own
  `cost_modifiers/_documentation.md`.
- `references/small-systems.md`: game rules (self-documented format),
  ideologies (family vs sub-ideology), buildings (modifier scope split,
  enable_for_controllers).
- Coverage map: peace_conference, buildings, game_rules, ideologies move
  to covered. Remaining uncovered: intelligence_agencies, names,
  autonomous_states, opinion_modifiers, wargoals, occupation_laws,
  medals, continuous_focus, combat_tactics, terrain, map_modes,
  difficulty_settings, defines.
- Register 134 claims; 22 references.

## 0.13.0 — Core references deepened to production depth

Goal: an AI can write complete, correct code for the five core systems
from a single reference read. Every table below is a vanilla census, not
memory:

- `events.md`: complete event field table (frequency-ranked, 24 fields
  incl. hidden, fire_for_sender, timeout_days, months), conditional
  multi-desc syntax, complete option field set.
- `national-focus.md`: complete focus field table (29 fields with vanilla
  frequencies, incl. will_lead_to_war_with, allow_branch, dynamic,
  enable_automatic_bypass).
- `ideas-and-modifiers.md`: slot-level fields (designer/law slots, ledger,
  politics_tab), full idea body incl. `rule` grants and
  `targeted_modifier`; the "three keyword spaces" (modifiers vs rules vs
  effects) trap documented.
- `localisation.md`: scope-getter census (GetName 289, GetAdjective 241,
  GetLeader 200, GetNameDef 133...) and the two display traps.
- `gfx-and-assets.md`: complete SpriteType fields (noOfFrames icon strips
  + 11-field animation family + effectFile), the £-strip connection.
- Register 126 claims; all references stay under the 400-line limit.

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
