# `common/` directory index

Navigational map of every entry in the game's `common/` folder — what it
holds and where this skill covers it. File counts measured on a real
**1.20.0.0** install (2026-11-21); expect drift per patch (re-derive with
`scripts/stale_check.py`). Purposes here are one-line orientation only —
behavioral claims live in the linked references and the claims register.

Gap tiers match [docs/coverage.md](../../../docs/coverage.md):
**gap (script)** = worth documenting next, **gap (AI)** = advanced,
**gap (cos)** = cosmetic/UI tier, out of scope like `gfx/` or `sound/`.

| Entry | Files | Holds | Covered by |
|---|---|---|---|
| `abilities/` | 6 | unit-leader ability definitions | characters.md |
| `acclimatation.txt` | 1 | weather-adaptation training tiers for units | gap (script) |
| `aces/` | 1 | air ace definitions | gap (script) |
| `achievements.txt` | 1 | Steam achievement triggers | gap (cos) |
| `ai_areas/` | 1 | AI naval/area prioritization | gap (AI) |
| `ai_attitudes.txt` | 1 | how AI weighs attitudes between countries | gap (AI) |
| `ai_equipment/` | 23 | AI equipment production priorities | gap (AI) |
| `ai_faction_theaters/` | 2 | AI faction-level theater strategy | gap (AI) |
| `ai_focuses/` | 8 | AI research-weight personas | ai-strategy.md |
| `ai_navy/` | 26 | AI naval composition/doctrine logic | gap (AI) |
| `ai_personalities.txt` | 1 | AI personality weights for AI strategies | gap (AI) |
| `ai_strategy/` | 51 | country AI strategies (role, research, production) | ai-strategy.md |
| `ai_strategy_plans/` | 130 | concrete AI area plans feeding strategies | ai-strategy.md |
| `ai_templates/` | 16 | AI division-template construction rules | ai-strategy.md |
| `alerts.txt` | 1 | on-screen alert definitions | gap (cos) |
| `autonomous_states/` | 21 | autonomy levels (puppet, dominion, ...) | misc-systems.md |
| `bookmarks/` | 2 | title-screen scenario cards | small-systems.md |
| `bop/` | 10 | Balance of Power definitions | balance-of-power.md |
| `buildings/` | 2 | building definitions + modifiers | small-systems.md |
| `characters/` | 233 | leaders, advisors, commanders, operatives | characters.md |
| `collections/` | 3 | profile item collections | gap (cos) |
| `combat_tactics.txt` | 1 | combat tactic definitions and counters | misc-systems.md |
| `continuous_focus/` | 1 | repeatable continuous focus tree | national-focus.md |
| `countries/` | 442 | per-country colors, history hooks, cosmetics | map-states-and-history.md |
| `country_leader/` | 4 | legacy leader portraits/politics data | characters.md |
| `country_tag_aliases/` | 1 | alternate tags mapping to canonical tags | gap (script) |
| `country_tags/` | 2 | canonical TAG list + colors | map-states-and-history.md |
| `decisions/` | 147 | decisions, missions and categories | decisions.md |
| `defines/` | 3 | engine-tuning Lua (NDefines) — blast radius | misc-systems.md (warning) |
| `difficulty_settings/` | 1 | custom-difficulty per-country toggles | small-systems.md |
| `doctrines/` | 27 | air/naval doctrine trees | tech-tree.md |
| `dynamic_modifiers/` | 12 | reusable named modifier stacks | ideas-and-modifiers.md |
| `equipment_groups/` | 2 | equipment archetypes grouping | mio.md, units-and-equipment.md |
| `event_modifiers.txt` | 1 | event-applied modifier templates | gap (script) |
| `factions/` | 30 | faction definitions and rules | gap (script) |
| `focus_inlay_windows/` | 7 | focus-tree inlay UI windows | gap (cos) |
| `frontend/` | 1 | main-menu/front-end definitions | gap (cos) |
| `game_rules/` | 1 | game-setup rule options | small-systems.md |
| `generation/` | 1 | name/asset generation rules | gap (cos) |
| `graphicalculturetype.txt` | 1 | graphical culture typing | gap (cos) |
| `idea_tags/` | 1 | idea slot categories and ledger | ideas-and-modifiers.md |
| `ideas/` | 214 | national spirits, laws, designers, advisors | ideas-and-modifiers.md |
| `ideologies/` | 1 | ideology families and sub-types | small-systems.md |
| `intelligence_agencies/` | 1 | agency definitions | operations.md |
| `intelligence_agency_upgrades/` | 2 | agency branch upgrades | operations.md |
| `map_modes/` | 1 | scripted map modes (+ game's own doc) | small-systems.md |
| `medals/` | 1 | country medal definitions | misc-systems.md |
| `military_industrial_organization/` | 63 | MIOs (design companies) | mio.md |
| `modifier_definitions/` | 2 | custom modifier type declarations | ideas-and-modifiers.md |
| `modifiers/` | 5 | static modifier stacks (incl. difficulty) | ideas-and-modifiers.md |
| `msgrdk_achievements.json` | 1 | NOT vanilla — third-party leftover in one install; never document from it | — |
| `mtth/` | 1 | mean-time-to-happen blocks for ops/agency AI | gap (script) |
| `names/` | 1 | ace + operation name pools | small-systems.md |
| `national_focus/` | 82 | national focus trees | national-focus.md |
| `occupation_laws/` | 1 | occupation policy definitions | misc-systems.md |
| `on_actions/` | 19 | lifecycle/global event hooks | variables-and-scripting.md |
| `operation_phases/` | 17 | agency operation phase logic | gap (script) |
| `operation_tokens/` | 2 | operation token definitions | gap (script) |
| `operations/` | 7 | intelligence operations | operations.md |
| `opinion_modifiers/` | 14 | diplomatic opinion modifiers | misc-systems.md |
| `peace_conference/` | 37 | peace conference costs and AI desires | peace-conference.md |
| `profile_backgrounds/` | 1 | profile UI backgrounds | gap (cos) |
| `profile_pictures/` | 1 | profile UI pictures | gap (cos) |
| `raids/` | 10 | raid definitions (air/naval/land strikes) | raids.md |
| `region_colors.txt` | 1 | strategic-region map colors | gap (cos) |
| `resistance_activity/` | 1 | occupation resistance behavior | gap (script) |
| `resistance_compliance_modifiers/` | 2 | compliance-tier modifiers | gap (script) |
| `resources/` | 2 | strategic resource definitions | gap (script) |
| `ribbons/` | 1 | profile ribbon rewards | gap (cos) |
| `scientist_traits/` | 2 | special-project scientist traits | gap (script) |
| `scorers/` | 4 | reusable AI scoring blocks | gap (script) |
| `script_constants/` | 5 | reusable script constants (+ game's own doc) | variables-and-scripting.md |
| `script_enums.txt` | 1 | enum value lists usable in script params | variables-and-scripting.md |
| `scripted_diplomatic_actions/` | 1 | agent-triggered diplomatic actions | gap (script) |
| `scripted_effects/` | 52 | reusable script effect blocks | variables-and-scripting.md |
| `scripted_guis/` | 21 | scripted UI front-ends | scripted-gui.md |
| `scripted_localisation/` | 43 | dynamic text generation | localisation.md |
| `scripted_triggers/` | 55 | reusable script trigger blocks | variables-and-scripting.md |
| `special_projects/` | 17 | research facilities and projects | special-projects.md |
| `state_category/` | 13 | state categories and their modifiers | map-states-and-history.md |
| `strategic_locations/` | 2 | naval strategic locations | gap (script) |
| `synchronized_dynamic_tokens/` | 1 | synced dynamic text tokens | gap (cos) |
| `technologies/` | 13 | land/air/naval technology trees | tech-tree.md |
| `technology_sharing/` | 11 | faction technology sharing rules | gap (script) |
| `technology_tags/` | 1 | technology category tags | tech-tree.md |
| `terrain/` | 1 | terrain types and combat modifiers | map-modding.md (orientation) |
| `timed_activities/` | 1 | timed country activities | gap (script) |
| `triggered_modifiers.txt` | 1 | condition-applied static modifiers | gap (script) |
| `unit_leader/` | 13 | unit-leader traits and assignment rules | characters.md, units-and-equipment.md |
| `unit_medals/` | 1 | unit-level medals | gap (cos) |
| `unit_tags/` | 1 | naval/unit name tags | gap (cos) |
| `units/` | 298 | sub_units, equipment, templates | units-and-equipment.md |
| `wargoals/` | 1 | wargoal types and costs | misc-systems.md |
| `weather.txt` | 1 | weather system definitions | gap (script) |

## Usage notes for agents

- When a mod file lands in a directory you do not recognize, look it up
  here first; if it is a gap tier, say so and check the actual vanilla
  files in the user's install instead of guessing from memory.
- File counts drift with every patch — the number is an orientation, not
  a contract. `scripts/stale_check.py` tells you whether the skill's
  verified version matches the install.
