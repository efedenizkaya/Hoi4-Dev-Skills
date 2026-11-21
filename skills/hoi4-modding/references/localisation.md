# Localisation

Files: `localisation/<language>/<anything>_l_<language>.yml` — the
`_l_<language>` suffix is what registers the file. Languages: `english`,
`german`, `french`, `spanish`, `russian`, `polish`, `braz_por`, `japanese`,
`simp_chinese` (+ `replace/` for vanilla-key overrides).

CLAIM(loc-languages)

## File contract (violations are the #1 loc bug)

```yml
l_english:
 mymod.1.t:0 "An Eventful Day"
 mymod.1.d:0 "Something happened to [Root.GetNameDef].\nMore text on a new line."
 mymod.1.a:0 "Proceed"
```

- **UTF-8 with BOM** — no BOM, no load. Windows editors "save as UTF-8"
  without BOM by default; the validator warns (`loc-file-encoding`).
  CLAIM(loc-bom)
- One `l_english:` header line; entries indented with **one space**; keys
  end with `:<version>` (`:0`, `:1` — version is cosmetic).
- `\n` newline; escape `"` as needed inside the quoted text.
- Descending files override earlier ones (load order); `localisation/
  replace/` overrides vanilla keys of every language dir with one file.

CLAIM(loc-file-contract)

## Inline commands

From vanilla text — the common set:

- Colors: `§R` red, `§Y` yellow, `§G` green, `§B` blue, `§W` white… closed
  with `§!`. CLAIM(loc-color-codes)
- Scope objects: `[Root.GetNameDef]`, `[From.GetLeader]`, `[This.GetName]` —
  objects and their getters are documented in the game's
  `documentation/loc_objects_documentation.md` (Country, State, Character,
  UnitLeader, Faction, …). Use those names, do not invent getters.
  CLAIM(loc-objects-doc)
- Icons: `£token` from the interface icon sheets, optional width
  `£resources_strip|5` — NOT `@icon!` (that is another Paradox game).
  CLAIM(loc-icon-syntax)
- Dynamic values: `$variable$` renders a variable/scripted value
  (vanilla achievements loc: `$upgrade_psycho_warfare$`).
  CLAIM(loc-dynamic-values)

## Scripted localisation

`common/scripted_localisation/*.txt` — computed text:

```txt
defined_text = {
	name = scripted_loc_mymod_key
	text = {
		trigger = { has_war = yes }
		localisation_key = mymod_at_war
	}
	text = {
		trigger = { always = yes }
		localisation_key = mymod_at_peace
	}
}
```

Keys must exist in localisation; the first matching `text` block wins.
Game-side formatters (e.g. `advisor_desc`, `idea_name`) are documented in
`documentation/loc_formatter_documentation.md` and invoked as
`custom_effect_tooltip = formatter|arg`. CLAIM(scripted-loc)

## Fonts and characters

The default fonts do not cover every script — characters outside the
language's font set render as boxes; test any non-Latin text in the target
language folder, not in english. CLAIM(loc-font-coverage) `[unverified]`

## Verification steps

1. `python tools/validate.py <mod_dir>` — BOM warnings, missing keys used
   by events.
2. Grep your keys against usage: every `name`/`desc`/`title` reference
   resolves (validator does this for events).
3. In-game: open the event/idea; `[Root.GetNameDef]` wrong scope shows a
   literal tag like `GER` instead of "Germany" — a scoping bug, not a loc
   bug.

## Scope object getter census (vanilla english loc, 1.19.4.1)

Frequency of `[Scope.Getter]` usage across vanilla english files:

| Getter | Freq | Returns |
|---|---|---|
| `[Root.GetName]` / `[From.GetName]` | 289 | country/state name |
| `[Root.GetAdjective]` | 241 | adjectival form ("German") |
| `[Root.GetLeader]` | 200 | leader name |
| `[Root.GetNameDef]` | 133 | definite-form name ("Germany") |
| `[Root.GetNameDefCap]` | 81 | capitalized definite form |
| `[Root.GetRulingParty]` | 50 | ruling party name |
| `[Root.GetFactionName]` | 42 | faction name |
| `[Root.GetCallsign]`, `GetMissionRegion`, `GetRulingIdeology`, `GetFullName`, `GetHerHis`, `GetCommunistParty`, loyalty-level getters | rare | characters and ideologies included |

Full object→getter tables: the game's
`documentation/loc_objects_documentation.md`. Use only getters listed
there; a wrong getter renders literally. CLAIM(loc-getter-census)

### The two display traps

- `[Root.GetName]` on a country gives the short name; `[Root.GetNameDef]`
  gives the grammatical definite form — vanilla alternates them constantly.
- Character loc uses the character object: `[Root.GetLeader]` is the safe
  accessor; `[CHARACTER_token.GetName]` also works after the character is
  in scope. CLAIM(loc-display-traps)

## Syncing missing translations

`scripts/loc_sync.py --mod <dir> --lang german[,french,...]` generates
`zz_sync_l_<lang>.yml` stub files: every key present in english but
missing from the language, prefilled with the ENGLISH text. Existing
translations anywhere in the language folder are respected, user files
are never touched, and re-running never overwrites your edits. Pair with
`scripts/loc_report.py` for the coverage numbers. CLAIM(loc-sync-tool)
