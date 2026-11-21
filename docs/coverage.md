# Reference coverage map

Honest inventory: every system in the game's `common/` folder (94 entries,
re-census 2026-11-21, game 1.20.0.0) and whether this skill covers it.
`covered` = a reference file grounds it; `partial` = mentioned inside
another reference; `uncovered` = not documented here yet. This map exists
so contributors can pick work and users can check before trusting.

## Covered

| System | Reference |
|---|---|
| `ai_strategy`, `ai_strategy_plans`, `ai_templates`, `ai_schemes` | [ai-strategy.md](../skills/hoi4-modding/references/ai-strategy.md) |
| `characters` | [characters.md](../skills/hoi4-modding/references/characters.md) |
| `country_tags`, `country_colors` | [map-states-and-history.md](../skills/hoi4-modding/references/map-states-and-history.md) |
| `decisions` | [decisions.md](../skills/hoi4-modding/references/decisions.md) |
| `dynamic_modifiers`, `ideas`, `idea_tags`, `modifier_definitions`, `modifiers` | [ideas-and-modifiers.md](../skills/hoi4-modding/references/ideas-and-modifiers.md) |
| `military_industrial_organization` | [mio.md](../skills/hoi4-modding/references/mio.md) |
| `national_focus` | [national-focus.md](../skills/hoi4-modding/references/national-focus.md) |
| `on_actions`, `scripted_effects`, `scripted_triggers` | [variables-and-scripting.md](../skills/hoi4-modding/references/variables-and-scripting.md) |
| `script_constants/`, `script_enums.txt` | [variables-and-scripting.md](../skills/hoi4-modding/references/variables-and-scripting.md) |
| `scripted_guis` | [scripted-gui.md](../skills/hoi4-modding/references/scripted-gui.md) |
| `scripted_localisation` | [localisation.md](../skills/hoi4-modding/references/localisation.md) |
| `technologies`, `technology_tags`, `land_doctrines` | [tech-tree.md](../skills/hoi4-modding/references/tech-tree.md) |
| `units` (sub_units + equipment, 298 files @1.20) | [units-and-equipment.md](../skills/hoi4-modding/references/units-and-equipment.md) |
| `bop` (Balance of Power) | [balance-of-power.md](../skills/hoi4-modding/references/balance-of-power.md) |
| `raids` | [raids.md](../skills/hoi4-modding/references/raids.md) |
| `operations` | [operations.md](../skills/hoi4-modding/references/operations.md) |
| `peace_conference` (37 files @1.20) | [peace-conference.md](../skills/hoi4-modding/references/peace-conference.md) |
| `game_rules`, `ideologies`, `buildings` | [small-systems.md](../skills/hoi4-modding/references/small-systems.md) |
| `bookmarks`, `names`, `difficulty_settings`, `map_modes` | [small-systems.md](../skills/hoi4-modding/references/small-systems.md) |
| `special_projects` (17 files @1.20) | [special-projects.md](../skills/hoi4-modding/references/special-projects.md) |
| `map/` (high-risk orientation) | [map-modding.md](../skills/hoi4-modding/references/map-modding.md) |
| `ai_focuses` (research-weight personas) | [ai-strategy.md](../skills/hoi4-modding/references/ai-strategy.md) |
| `.mod` descriptors, load order, overrides | [mod-structure.md](../skills/hoi4-modding/references/mod-structure.md) |
| debugging, `-debug`, logs | [debugging-and-logs.md](../skills/hoi4-modding/references/debugging-and-logs.md) |
| control flow, iteration, event targets | [control-flow.md](../skills/hoi4-modding/references/control-flow.md) |
| symptom-first triage | [symptoms.md](../skills/hoi4-modding/references/symptoms.md) |

## Partial (mentioned inside other references)

- `state_category`, `defines` (referenced where relevant)
- `equipment_groups` (referenced from MIO/units pages)
- `country_leader` (folded into characters.md)

## Uncovered (1.20.0.0 census: 37 systems with no reference text — pick from here)

Ranked by modder value. `defines` stays partial (blast-radius warning in
[misc-systems.md](../skills/hoi4-modding/references/misc-systems.md)).

Script-facing — worth documenting next (35 systems left; the index of
every entry, covered or not, lives in
[common-directory-index.md](../skills/hoi4-modding/references/common-directory-index.md)):

| System | Notes |
|---|---|
| `triggered_modifiers.txt`, `event_modifiers.txt` | conditional modifier application, vanilla grammar |
| `scripted_diplomatic_actions/` | scripted_guis' diplomacy sibling |
| `resistance_activity/`, `resistance_compliance_modifiers/` | occupation internals — pairs with occupation_laws (misc-systems.md) |
| `country_tag_aliases/` | tag aliases — tag-mod compatibility surface |
| `technology_sharing/` | faction tech sharing — pairs with tech-tree.md |
| `scorers/`, `mtth/` | AI scoring + MTTH blocks used by operations/agency AI |
| `operation_phases/`, `operation_tokens/`, `strategic_locations/` | operations internals — pairs with operations.md |
| `scientist_traits/` | special-project scientists — pairs with special-projects.md |
| `acclimatation.txt` | weather adaptation for units |

AI-internal (advanced, lower priority): `ai_areas/`, `ai_equipment/`,
`ai_faction_theaters/`, `ai_navy/`, `ai_attitudes.txt`,
`ai_personalities.txt`.

Cosmetic/UI tier (out of scope like `gfx/`, `sound/`, `tutorial/`):
`frontend/`, `profile_backgrounds/`, `profile_pictures/`, `collections/`,
`ribbons/`, `unit_medals/`, `focus_inlay_windows/`, `region_colors.txt`,
`graphicalculturetype.txt`, `alerts.txt`, `generation/`, `unit_tags/`.

Not vanilla: one install in the wild carried `msgrdk_achievements.json` —
a third-party leftover. Never document from it.

Non-`common` surfaces: `map/` deep-editing has an orientation page
([map-modding.md](../skills/hoi4-modding/references/map-modding.md));
`gfx/` pipelines, `sound/`/`music/`, `tutorial/` remain out of scope.

## Tooling coverage

| Tool | Job |
|---|---|
| `scripts/extract.py` | game docs → JSON |
| `scripts/validate.py` | lint + silent-failure rules |
| `scripts/error_triage.py` | log classify/diff |
| `scripts/find.py` | identifier index |
| `scripts/version_diff.py` | patch migration diff |
| `scripts/override_audit.py` | vanilla shadow inventory |
| `scripts/loc_report.py` | multi-language coverage |
| `scripts/new_mod.py` | mod skeleton |
