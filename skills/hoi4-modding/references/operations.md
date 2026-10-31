# Intelligence agency operations

La Résistance-era mechanic. Files: `common/operations/*.txt` — vanilla
sorts them by (required operatives, network strength).

CLAIM(operations-files)

## Anatomy (vanilla `operation_rescue_operative`)

```txt
operation_rescue_operative = {
	icon = GFX_operations_rescue_captured_operative
	map_icon = GFX_operations_rescue_captured_operative_map
	name = operation_rescue_operative        # loc keys: name + <name>_desc
	desc = operation_rescue_operative_desc
	priority = 0

	days = 35                                # duration
	network_strength = 30                    # required intel network strength
	operatives = 1                           # required operative count
	prevent_captured_operative_to_die = yes  # operation-specific flags

	visible = {
		FROM = { has_captured_operative = ROOT }   # FROM = target country
	}
	available = { ... }
	# setup, on_start, on_..., completion / failure effect blocks
}
```

CLAIM(operations-anatomy)

## Rules that bite

- `visible`/`available` run with **FROM = the target country** — the
  vanilla rescue operation checks `FROM.has_captured_operative = ROOT`.
  CLAIM(operations-from-target)
- Operatives and network strength are hard gates: a `days`/`network_strength`
  mismatch with the operative count changes the UI sorting (vanilla sorts
  by operatives, then network strength).
- Icons are `GFX_operations_*` sprites; missing ones show placeholders
  without logging (see [gfx-and-assets.md](gfx-and-assets.md)).

## Verification

1. Validator; 2. in-game: agency panel → operations list (requires an
   agency + La Résistance); 3. triage for loc/`invalid-scope` classes.
