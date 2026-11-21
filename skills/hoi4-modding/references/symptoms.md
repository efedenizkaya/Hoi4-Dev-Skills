# Symptom-first troubleshooting

Start from what the player sees, map it to the likely cause and the tool
that confirms it. Finding labels (`definite` / `probable` / `heuristic` /
`intentional`) are defined in SKILL.md.

| Symptom | Likely causes (most common first) | Confirm with | Label |
|---|---|---|---|
| "Event has no ID" / event popup shows `myevent.1` raw text | loc keys missing; loc file has no BOM and was not loaded | validator `missing-loc-key`; game `loc-error` class | definite |
| Focus tree does not appear in game | tree's `country` weight block picks nothing; duplicate focus id; file does not override vanilla (wrong path/filename); `default` flag misuse | validator `duplicate-focus-id`; in-game after fixing weight block | probable → definite |
| Focus tree shows but branches are locked | `available` vs `bypass` confusion; unidirectional `mutually_exclusive`; prerequisite targets another tree's focus | validator `missing-focus-prerequisite`, `unidirectional-mutual-exclusive` | definite |
| Loc key shows as raw text in tooltip | key typo; key defined in the wrong language folder; file not `_l_english` suffixed; missing BOM | validator `missing-loc-key`, `loc-file-encoding` | definite |
| Icon shows as question mark / placeholder | sprite name not defined in any `interface/*.gfx` (typos do NOT log); texture file missing (DOES log) | `error.log` `missing-entity` class for files; visual check for names | probable |
| Event never fires | `is_triggered_only` missing with empty trigger; firing effect targets wrong scope; on_action hook name misspelled (silent) | console `event <ns>.<id>`; triage | heuristic |
| Decision button greyed out | `available` fails (check its triggers one by one); cost unpaid; `days_re_enable` cooldown | console `pp` / `cp`, then re-check | definite |
| "Invalid tech" in error.log at game start | `set_technology` references a tech renamed/removed by a mod override | triage `invalid-tech` class; grep the tech id | definite |
| Effect does nothing, no error | unknown modifier name (silent no-op); `var:` missing on a token (logs `invalid database object`); effect not in this game version | `--data` statement-name check; triage `invalid-database-object` | probable |
| Mod works alone, breaks in playset | file collision with another mod (same relative path replaces it); load order lost | both mods' file lists; `setup.log` | probable |
| Whole mod fails to load | parse error somewhere upstream — one bad brace kills a file | validator `unbalanced-braces`/`unbalanced-quotes`; triage `parse-error` | definite |

## The two-question shortcut

1. Does `scripts/validate.py` report anything new? Fix those first.
2. Does `scripts/error_triage.py --against baseline.log` show a positive
   delta? Those are your regressions.

If both are clean and the symptom persists, it is in the UI/runtime layer —
scope flow, positioning, or gfx names. See
[variables-and-scripting.md](variables-and-scripting.md) and
[national-focus.md](national-focus.md).
