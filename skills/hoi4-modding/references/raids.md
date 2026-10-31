# Raids

Province-targeted strike mechanic (1.14+, By Blood Alone/AAT era). Files:
`common/raids/*.txt` + `common/raids/categories/*.txt`. The game ships its
own doc at `common/raids/_documentation.md` — the authoritative source.

CLAIM(raids-files)

## Two databases

**Category** (where raids appear):

```txt
raid_category_id = {
	intel_source = air            # air | naval | army | civilian
	visible = { ... }             # country scope
	available = { ... }
	free_targeting = yes          # target any province (nuclear-style);
	                              # raid types still need province = any
}
```

**Type** (the raid itself):

```txt
facility_strike = {
	category = raid_category_id
	days_to_prepare = 90

	ai_will_do = { base = 2 modifier = { factor = 0 is_major = no } }

	command_power = 20                # CP allocation cost
	arrow = { type = line }           # line | ballistic | air | naval | land

	unit_icon = GFX_ref               # icon trio: unit / target / equipment
	target_icon = GFX_ref
	equipment_icon = GFX_ref
	launch_sound = SFX_ref

	unit_model = {
		entity = entity_name          # resolution order: country-specific →
		default_entity = default_name # culture → base → default
		# equipment = air_transport   # only air equipment supported
	}
	# target requirements, effects on success, etc. — see the game doc
}
```

CLAIM(raids-anatomy)

## Rules that bite

- Icon fallback chain is automatic: `GFX_raid_type_icon_{raid_name}` unless
  `custom_map_icon` overrides it. CLAIM(raids-icon-fallback)
- `free_targeting` on the category is necessary — but not sufficient — for
  free province targeting; the raid type must also allow `province = any`.
- `unit_model.entity` follows the country → culture → base → default
  lookup; missing entities fall back silently unless no default exists.
  CLAIM(raids-entity-lookup)

## Verification

1. Validator; 2. in-game raid tab under the matching intel source; 3.
   triage for `missing-entity` (unit models) classes.
