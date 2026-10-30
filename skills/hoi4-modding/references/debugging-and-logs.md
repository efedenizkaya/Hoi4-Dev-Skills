# Debugging and logs

## Debug mode

Launch option `-debug` (Steam → game properties → launch options, or a
shortcut to `hoi4.exe -debug`). It loads the game's internal debug content
(`_debug_spirits`, `_debug_decisions`, `debug_events`) and enables the debug
console commands. Debug mode is required for the console commands listed in
`documentation/console_commands_documentation.md` such as
`Focus.AutoComplete`, `Focus.IgnorePrerequisites`, `Focus.NoChecks`.

CLAIM(debug-mode-loads)

## What lands in the logs folder

`Documents/Paradox Interactive/Hearts of Iron IV/logs/` after any run:

| File | Use |
|---|---|
| `error.log` | **the** modding signal: invalid effects, scopes, ids, loc, entities |
| `game.log` | load summary (defines, provinces, history execution) |
| `setup.log` | full asset/idea/decision load lines — counts per file |
| `system_debug.log` | interface/GUI layout errors |
| `memory.log`, `ai.log` | performance and AI traces |

The game also ships its own API docs at `<game>/documentation/`
(`effects_documentation.md`, `triggers_documentation.md`,
`modifiers_documentation.md`, …) — regenerated every patch; `tools/extract.py`
turns them into JSON. CLAIM(logs-table)

## error.log line format

```
[HH:MM:SS][game.date][source.cpp:line]: message
[HH:MM:SS][no_game_date]: message            # source sometimes absent
```

CLAIM(error-log-format)

## Triage workflow (the loop)

1. Baseline: copy the current `error.log` before changing anything.
2. Apply the change, launch once (with `-debug`), close to menu or desktop.
3. `python tools/error_triage.py logs/error.log --against baseline.log`
   - class deltas: only positives need attention
   - "changed groups" section: the exact new messages
4. Map class → fix:
   - `invalid-scope`: effect used in a scope it does not support (check the
     effect's `Supported Scopes` in `effects.json`)
   - `invalid-database-object`: an identifier used where a database object
     is expected — usually a variable used without `var:` CLAIM(var-prefix)
   - `invalid-tech`: `set_technology` in history files referencing a
     nonexistent tech id
   - `missing-entity`: gfx entity referenced but not defined (often vanilla
     graphics db expectations)
   - `loc-error`: missing/invalid localisation
5. Repeat until the delta against baseline is clean.

## Reading crash logs

`crashes/` folders in the user directory hold crash dumps; for script-caused
crashes `error.log` plus the last-modified mod files usually identify the
culprit faster than the dump. Reproduce with only your mod enabled before
blaming load order.

## Console quick list (debug mode)

`event <ns>.<id>` (fire event), `annex <tag>`, `focus.autocomplete`,
`Focus.NoChecks`, `reload <file>` (hot-reload some file types),
`tdebug` (tooltip debug info). Full list: `documentation/
console_commands_documentation.md`. CLAIM(console-list)
