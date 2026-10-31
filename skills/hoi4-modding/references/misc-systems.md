# Small systems part 2

The remaining single-file systems, one section each. All field lists are
vanilla-grounded (1.19.4.1).

## Opinion modifiers (`common/opinion_modifiers/*.txt`)

```txt
opinion_modifiers = {
	faction_traitor = { value = -75 }
	faction_traitor_trade = { trade = yes value = -40 }   # affects trade opinion
}
```

Applied with `add_opinion_modifier = { target = X modifier = Y }`;
`trade = yes` splits the effect into the trade-opinion channel.
CLAIM(opinion-modifiers)

## Wargoals (`common/wargoals/*.txt`)

```txt
wargoal_types = {
	take_state = {
		# PREV = original target country; ROOT = goal owner country
		allowed = { ... }
		available = { ... }
		take_states = { ... }            # which peace actions the goal unlocks
		generate_base_cost = 200
		generate_per_state_cost = 50
	}
}
```

Scope contract documented in-file: `PREV` = target, `ROOT` = goal owner.
CLAIM(wargoals)

## Occupation laws (`common/occupation_laws/*.txt`)

The vanilla file is a commented template: `tooltip` (loc), `icon`
("GFX_icon:5" — frame in the strip), `sound_effect`, plus
`available`/`modifier` blocks per law. CLAIM(occupation-laws)

## Continuous focus (`common/continuous_focus/*.txt`)

```txt
continuous_focus_palette = {
	id = generic_focus
	country = { factor = 1 }        # tree-selection pattern (see national-focus.md)
	default = yes
	reset_on_civilwar = no
	# continuous focus entries with cost/duration per position
}
```

CLAIM(continuous-focus)

## Medals (`common/medals/00_medals.txt`)

`medals = { <token> = { name/description loc keys, frames/colors for the
ribbon sprite layers } }` — purely cosmetic career-profile awards.
CLAIM(medals)

## Intelligence agencies (`common/intelligence_agencies/*.txt`)

Custom agency NAMES + LOGOS only (mechanics live in
`intelligence_agency_upgrades` and operations):

```txt
intelligence_agency = {
	picture = GFX_intelligence_agency_logo_usa
	names = { "Office of Strategic Services" }   # loc entry or literal; random pick
	default = { tag = USA }
	available = { original_tag = USA }
}
```

CLAIM(intelligence-agencies)

## Combat tactics (`common/combat_tactics.txt`)

Tactic names MUST start with `tactic_` to work with techs (in-file note);
`phases` list defines the combat phase order. CLAIM(combat-tactics)

## Terrain (`common/terrain/00_terrain.txt`)

`categories = { <terrain> = { color, ... } }` plus terrain definitions
with movement/combat modifiers — map-adjacent; changing existing terrain
is safe-ish, adding new terrain touches map files. CLAIM(terrain)

## Autonomous states (`common/autonomous_states/*.txt`)

Puppet/subject levels: `autonomy_state = { id, is_puppet,
min_freedom_level, manpower_influence, use_overlord_color, rule = {...} }`
— the autonomy ladder's rungs. CLAIM(autonomous-states)

## defines, difficulty_settings, names

- `defines/` — engine constants (Lua). Overriding one value changes global
  behavior; always comment the vanilla value. **High blast radius.**
- `difficulty_settings/` — per-difficulty modifier bundles.
- `names/` — unit/leader name pools per culture/tag.

All three: change with care, verify in game; no validator rules cover
them. CLAIM(defines-blast-radius)
