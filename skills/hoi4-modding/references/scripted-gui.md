# Scripted GUIs

Interactive custom UIs. Two halves: a **script** in
`common/scripted_guis/*.txt` (logic) and a **window** declared in an
`interface/*.gui` file (layout). The game ships its own authoritative doc
at `common/scripted_guis/_documentation.md` — this page distills it.

CLAIM(sgui-files)

## Minimal pair

```txt
# common/scripted_guis/mymod_ui.txt
scripted_gui = {
	mymod_ui = {
		context_type = decision_category   # see context list below
		window_name = "mymod_ui_window"    # must match the .gui container

		visible = { has_dlc = "Arms Against Tyranny" }

		effects = {
			mymod_button_click = { add_political_power = 10 }
		}
		triggers = {
			mymod_button_click_enabled = { check_variable = { mymod_ready > 0 } }
			mymod_icon_visible = { has_war = yes }
		}
		properties = {
			mymod_icon = { image = "[?mymod_frame|0]" }
		}
	}
}
```

```txt
# interface/mymod_gui.gui — the window the script binds to
guiTypes = {
	containerWindowType = {
		name = "mymod_ui_window"
		position = { x = 0 y = 0 }
		size = { width = 400 height = 180 }
		# buttons named mymod_button, icons named mymod_icon, ...
	}
}
```

CLAIM(sgui-minimal)

## context_type — where the UI lives

From the game's own doc (verbatim list): `player_context` (scope = player),
`selected_country_context`, `selected_state_context`,
`diplomacy_target_context`, `decision_category` (requires
`scripted_gui = <name>` in the category block; scope = player),
`diplomatic_action`, `national_focus_context`, `country_mapicon`,
`state_mapicon`. Vanilla census: `decision_category` dominates (19 of 20
scripted GUIs). CLAIM(sgui-context-types)
Vanilla census: `decision_category` dominates (19 of 20
scripted GUIs). CLAIM(sgui-context-types) CLAIM(sgui-context)

## Anchoring

By default the UI attaches to the main window (or the context's window).
`parent_window_token` accepts fixed tokens (`top_bar`, `decision_tab`,
`production_tab`, `army_ledger`, `tech_industry_folder`, …); otherwise
`parent_window_window = "container_name"` or
`parent_scripted_gui = "name"`. Map icons additionally need `map_mode` and
(optionally) `mapicon_targets`. CLAIM(sgui-anchoring)

## Binding rules (the part that fails silently)

- `effects` keys are **button names** in the .gui; suffixes
  `_click`, plus `_alt/_right/_ctrl/_shift` combinations
  (`mymod_button_right_click`).
- `triggers` keys must be `<button_name>_enabled` (disables) or
  `<element_name>_visible` (hides).
- `properties` target element names for image/frame/x/y — values may be
  scripted loc or variables.
- A name mismatch between script and .gui does nothing, silently — the
  validator's `find.py` is the way to check both sides exist.
  CLAIM(sgui-binding-silent)

## Scope

The GUI's scope depends on `context_type` (player for most contexts).
Effects inside `effects` run in that scope; use `ROOT`/`FROM`-style
re-scoping for the selected country/state.

## Verification steps

1. `python scripts/validate.py <mod_dir>` (braces; scripted GUI files are
   brace-dense).
2. `python scripts/find.py mymod_ui --mod <dir>` — script side and
   `window_name` counterpart both exist.
3. In-game: `setup.log`/`system_debug.log` carry .gui layout errors
   (positions, sizes); the UI itself must be checked visually.
