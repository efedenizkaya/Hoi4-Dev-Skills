# Map, states and country history

## State files

`history/states/<id>-<Name>.txt` — id matches the file number:

```txt
state={
	id=10
	name="STATE_10"                # loc key (STATE_10 defined in loc)
	manpower = 3089000
	state_category = large_city    # from common/state_category

	history={
		owner = POL
		victory_points = { 3544 25 }     # province_id, vp value
		buildings = {
			infrastructure = 4
			arms_factory = 6
		}
		add_core_of = POL                # claim: add_claim_of
	}

	provinces={ 402 467 524 3482 3544 }   # province ids owned by the state
	local_supplies=7.0
}
```

CLAIM(state-file-fields)

- `provinces` ids must exist in `map/definition.csv` — moving provinces is
  **map modding** (definition.csv, provinces.bmp, terrain.bmp, …) and out
  of scope here; re-assigning existing provinces between states is not.
  CLAIM(provinces-from-definition)
- Two states claiming the same province = load error; a state id reused =
  load error. The game's startup log (game.log `Loaded N provinces`,
  setup.log) is the check. CLAIM(state-uniqueness)

## Country history

`history/countries/<TAG> - Name.txt` (the space-dash name format matters
for tooling):

```txt
capital = 267
set_oob = "AFG_1936"                 # order of battle file in history/units/

set_technology = { infantry_weapons = 1 }

if = { limit = { has_dlc = "No Step Back" } ... }   # DLC branches are normal

add_ideas = AFG_some_starting_idea
recruit_character = AFG_someone
set_politics = { ruling_party = neutrality ... }
```

- Runs as an effect chain at game start in **that country's scope** — the
  real error.log lines to watch: `set_technology: Invalid tech`,
  `recruit_character: Character X cannot be assigned...`.
  CLAIM(country-history-effect-chain)
- OOB files (`history/units/*.txt`) define starting divisions/ships —
  large, unit-design-sensitive; regenerate when equipment names change.
  CLAIM(oob-files)

## Country tags

`common/country_tags/*.txt` (`TAG = "00_country_name_key"`); new tags need
common/country_colors + `gfx/flags` set + a country history file to exist
in-game. Tags are three letters (with digits allowed for rebels like
`00_` prefixed tags via `00_XXX` pattern — check vanilla
`common/country_tags/00_countries.txt` format before adding).
CLAIM(country-tags-file)

## Defining a new country — checklist

1. `common/country_tags/`: `MYC = "MYC_country_name"` (loc key).
2. `common/country_colors/`: map color entry.
3. `gfx/flags/MYC.tga` (+ medium/small), `gfx/flag_output/` builds cosmetic
   variants.
4. `history/countries/MYC - My Country.txt`: capital, state ownership in
   the relevant state files, OOB or none.
5. Localisation for the name key.
6. Verify: launch, `error.log` triage — tag/state/flag errors all surface
   in the first run.

## Strategic regions & supply

`map/strategicregions_*.csv`, supply nodes and railways (NSB+) live in
`map/` CSVs — treat as map modding: backup first, changes are
hard-to-diagnose in error.log. CLAIM(map-csv-risk)
