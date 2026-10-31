# Units, equipment and the division designer

The biggest system in `common/` (296 files). Two databases plus the
designer glue — and the game ships its own equipment documentation at
`common/units/equipment/_documentation.md`.

CLAIM(units-files)

## The three layers

| Layer | File | Role |
|---|---|---|
| **sub_units** (battalions/companies) | `common/units/<name>.txt` | the building blocks of divisions |
| **equipment types** | `common/units/equipment/*.txt` | what factories produce; archetypes + variants |
| **templates** | `history/units/*.txt` + `common/ai_templates/` | starting divisions; AI build plans |

A sub_unit *uses* equipment; a template *combines* sub_units. Renaming an
equipment id breaks every sub_unit referencing it **and** every in-game
stockpile, silently in saves.

CLAIM(units-layers)

## sub_unit anatomy (vanilla infantry)

```txt
sub_units = {
	infantry = {
		abbreviation = "INF"
		sprite = infantry                    # 2D sprite family
		map_icon_category = infantry         # infantry|armored|other / ship|transport|uboat
		priority = 600
		ai_priority = 200
		active = no                          # not selectable until enabled by tech/doctrine
		type = { infantry }                  # which equipment TYPE it consumes
		group = infantry
		categories = { category_front_line category_all_infantry }  # designer + AI filters
		# combat stats, terrain modifiers, need = { infantry_equipment = 100 } ...
	}
}
```

CLAIM(sub-unit-fields)

## Equipment types (from the game's own doc)

```txt
equipments = {
	infantry_equipment_0 = {
		year = 1918
		is_archetype = no
		archetype = infantry_equipment
		is_buildable = yes
		priority = 10
		type = { infantry }          # land / naval / air families, see doc
		max_military_factories = 5   # optional production cap
	}
}
```

- `is_archetype = yes` entries are the abstract parents the designer shows;
  concrete `archetype = X` children are the upgradeable tiers.
- `is_frame = yes` marks modular frames (tank chassis, ship hulls, plane
  frames) — NSB/BBA designer equipment uses `module_slots` defined in the
  same file; fixed slots start with `fixed_`.
- `ai_type` overrides the `type` used by AI unit_ratio strategies (e.g.
  carrier fighter vs land fighter, both `type = figher` — note the doc's
  spelling). CLAIM(equipment-fields)

## How mods interact with this system

- **New battalion**: new sub_unit + its equipment + tech
  `enable_subunits`/`enable_equipments` — all three or it stays invisible.
  CLAIM(unit-needs-tech)
- **New equipment tier**: child of an existing archetype (`parent`) so it
  inherits designer slots and upgrade paths.
- **Template changes** in history files: divisions reference
  `division_template` names; renaming a template breaks every OOB file
  using it. CLAIM(template-rename-breaks-oob)
- **Renaming ids** breaks saves (stockpiles reference equipment ids) —
  prefer additive tiers.

## Verification steps

1. `scripts/validate.py <mod_dir> --data extracted/<version>` — tech linkage
   is the usual break (`invalid-tech` class from history files).
2. `scripts/find.py <equipment_id> --mod <dir> --game-dir <game>` — see
   every sub_unit/template referencing it.
3. In game: production tab shows the archetype; division designer lists
   the battalion; error.log `missing-entity` for gfx issues.
