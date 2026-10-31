# Reference coverage map

Honest inventory: every system in the game's `common/` folder (94 entries,
census 2026-10-31, game 1.19.4.1) and whether this skill covers it.
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
| `scripted_guis` | [scripted-gui.md](../skills/hoi4-modding/references/scripted-gui.md) |
| `scripted_localisation` | [localisation.md](../skills/hoi4-modding/references/localisation.md) |
| `technologies`, `technology_tags`, `land_doctrines` | [tech-tree.md](../skills/hoi4-modding/references/tech-tree.md) |
| `units` (sub_units + equipment, 296 files) | [units-and-equipment.md](../skills/hoi4-modding/references/units-and-equipment.md) |
| `bop` (Balance of Power) | [balance-of-power.md](../skills/hoi4-modding/references/balance-of-power.md) |
| `raids` | [raids.md](../skills/hoi4-modding/references/raids.md) |
| `operations` | [operations.md](../skills/hoi4-modding/references/operations.md) |
| `.mod` descriptors, load order, overrides | [mod-structure.md](../skills/hoi4-modding/references/mod-structure.md) |
| debugging, `-debug`, logs | [debugging-and-logs.md](../skills/hoi4-modding/references/debugging-and-logs.md) |
| control flow, iteration, event targets | [control-flow.md](../skills/hoi4-modding/references/control-flow.md) |
| symptom-first triage | [symptoms.md](../skills/hoi4-modding/references/symptoms.md) |

## Partial (mentioned inside other references)

- `state_category`, `defines` (referenced where relevant)
- `equipment_groups` (referenced from MIO/units pages)
- `country_leader` (folded into characters.md)

## Uncovered (ranked by vanilla file count — pick from here)

| Files | System | Notes |
|---|---|---|
| 35 | `peace_conference` | complex, rarely modded by beginners |



| 6 | `abilities` | unit leader abilities |
| 2 | `buildings` | small; commonly modded |
| 2 | `bookmarks` | 1936 start bookmarks |
| 1 each | `game_rules`, `ideologies`, `intelligence_agencies`, `names`, `autonomous_states`, `opinion_modifiers`, `wargoals`, `occupation_laws`, `medals`, `continuous_focus`, `combat_tactics.txt`, `terrain`, `map_modes`, `difficulty_settings`, `defines` | mostly single-file systems |

Plus non-`common` surfaces: `map/` modding (provinces, terrain, supply),
`gfx/` pipelines, `sound/`/`music/`, `tutorial/` — out of scope for now,
documented as risky in map-states-and-history.md.

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
