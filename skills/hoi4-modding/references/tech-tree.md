# Technologies

Files: `common/technologies/*.txt` (`technologies = { ... }` wrapper),
categories in `common/technology_tags/`, doctrine trees in
`common/land_doctrines/` (and `naval_doctrines`, `air_doctrines`).

CLAIM(tech-files)

## Tech anatomy

```txt
@1918 = 0        # x-position aliases per year column (vanilla pattern)
@1924 = 1
...

technologies = {
	infantry_weapons = {
		enable_equipments = { infantry_equipment_0 }
		enable_equipment_modules = { tank_heavy_machine_gun }
		enable_subunits = { infantry }

		path = {
			leads_to_tech = infantry_weapons1
			research_cost_coeff = 1
		}

		research_cost = 1.5
		start_year = 1918
		folder = { name = infantry_folder position = { x = @1918 y = 0 } }

		categories = { infantry_weapons cat_mobile_warfare }

		dependencies = {  # optional hard dependency
			tech = some_tech focus = some_focus
		}

		doctrine = no          # techs only; doctrine trees separate

		path = { ... }         # repeatable

		on_research_complete = { ... }   # effects; also
		doctrine_effects = { ... }       # for doctrines
	}
}
```

CLAIM(tech-fields)

## Granting techs from script

`set_technology = { tech_name = 1 }` in history files or effects. The
game's own error for a bad name (real error.log class):
`history/countries/GER - Germany.txt:78: set_technology: Invalid tech` —
usually a vanilla tech renamed/removed by your mod or another mod's
override. CLAIM(set-technology-error)

## Rules that bite

- **Doctrines are not techs** — they live in their own tree files with
  `doctrine = yes` semantics and their own folder/category types; mixing
  the two is the classic "my tech doesn't show" bug. CLAIM(doctrine-separate)
- `start_year` gates **AI research ordering**, not availability.
  CLAIM(start-year-ai-ordering)
- `x`/`y` in `folder` use the `@year` aliases; a wrong alias (or one
  redefined mid-file) silently misplaces the whole tree.
- `research_bonus` from MIOs/ideas references `research_categories`
  matching this tech's `categories`.
- Adding a tech to an existing folder shifts nothing — positions are
  absolute; plan the grid before writing.

## Verification steps

1. Validator; then in game check the tree renders in the research tab.
2. error.log triage for `invalid-tech` class.
3. `set_technology` from console to test on_research_complete effects.
