# Scripted GUI kit

A minimal scripted GUI pair: the script (common/scripted_guis/) binds to
a window (interface/*.gui) by `window_name` — the two names must match
exactly or the binding fails silently. Attach it to a decision category
with `scripted_gui = mymod_panel_ui` in the category block.

1. Copy `common/`, `interface/` and `localisation/` into your mod.
2. `python scripts/validate.py <mod_dir>` — expect no findings.
3. In-game: the panel shows under the owning decision category while at
   war; the button grants 10 PP per click.
