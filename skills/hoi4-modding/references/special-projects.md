# Special projects (and research facilities)

Götterdämmerung-era system: research facilities developing projects with
prototype rewards. Files: `common/special_projects/{projects,project_tags,
specialization,prototype_rewards}/`. The game ships its own authoritative
doc: `common/special_projects/special_projects_documentation.md`.

CLAIM(sp-files)

## Anatomy (from the game's own doc)

```txt
special_project_id = {
	# loc fallback: TAG_<id> -> <id> (+ _desc), MIO-style
	narrative = { name = ... desc = ... }       # optional overrides
	icon = GFX_special_project_id               # optional

	special_project_parent = {                  # optional; ALL of these first
		special_project_1
		special_project_2
	}

	special_project_type = nuclear              # MANDATORY:
	# nuclear | aircraft (advanced/weapons) | electronics | tank | artillery
	# | rocket | missiles | naval — sets facility compatibility + art

	allowed = { ... }                           # default always
}
```

CLAIM(sp-anatomy)

## Rules that bite

- The **type** is mandatory and controls which facility develops the
  project and the default art; wrong type = project orphaned from
  facilities. CLAIM(sp-type-mandatory)
- Loc and icon follow the MIO fallback chain (`TAG_<id>` → `<id>` →
  default), so forgetful naming still renders.
- `prototype_rewards/` grant rewards on project breakthrough;
  `specialization/` tunes facility lines.

## Script surface

Facilities and project assignment use dedicated effects/triggers — check
`extracted/<version>/effects.json` for `special_project*` names per patch
(their set has grown since 1.16). CLAIM(sp-script-surface)

## Verification

1. Validator; 2. in game: facility view shows the project tree; 3. triage
   for `invalid-scope`/`invalid-database-object`.

## Specialization and prototype rewards

`specialization/specializations.txt`: `specialization_<domain> = { color
= {R G B} program_background = "GFX_..." }` — one per facility domain
(nuclear, naval, air, electronics, tank, artillery, rocket, missiles).

`prototype_rewards/*.txt`: weighted reward pools keyed by breakthrough
`threshold = { min max }`, with `weight = { base = N modifier = {...} }`
and `@base_reward_weight` aliases — failures and successes pick from the
same pool unless gated. Rewards fire `fire_only_once = no` style entries
per threshold. CLAIM(sp-specialization)
