# Small systems: game rules, ideologies, buildings, bookmarks, difficulty, map modes, names

Small systems, each light enough to master in minutes.

## Game rules (`common/game_rules/*.txt`)

Options on the game-rules screen, queryable from script via
`has_game_rule`. The vanilla file documents its own format:

```txt
rule_token = {
	name = "RULE_MY_RULE"            # loc keys
	required_dlc = "DLC Name"        # optional
	desc = "RULE_MY_RULE_DESC"
	group = "RULE_GROUP_MODS"        # filtering; multiple allowed
	icon = gfx_option_token          # optional

	option = {
		name = my_option
		text = "RULE_MY_RULE_OPTION"
		allow_achievements = no      # non-default options block achievements
	}
	default = {                      # overrides "first = default"
		name = my_option
	}
}
```

First option is the default unless `default = { }` overrides. Read from
script: `has_game_rule = { rule = rule_token option = my_option }` (used
heavily by AI plans — see [ai-strategy.md](ai-strategy.md)).
CLAIM(game-rules-format)

## Ideologies (`common/ideologies/*.txt`)

```txt
ideologies = {
	democratic = {
		types = { conservatism = {} liberalism = {} populism = {} ... }
		# rules, flags, faction modifiers, can_be_host etc. per ideology
	}
}
```

- Sub-ideologies (`types`) are what `set_politics = { ruling_party }`
  and `has_government` actually compare — the top-level ideology is the
  family. CLAIM(ideology-types)
- `has_government = fascism` matches the FAMILY; the specific subtype
  needs `has_government = { ruling_party = fascism sub_ideology = ... }`
  style checks — verify the exact trigger form against the version's
  triggers.json.

## Buildings (`common/buildings/00_buildings.txt`)

```txt
buildings = {
	arms_factory = {
		show_on_map = 6
		base_cost = 7200
		base_cost_conversion = 4000
		military_production = 1
		icon_frame = 2
		level_cap = { shares_slots = yes state_max = 20 }
		# country_modifiers / state_modifiers with
		# enable_for_controllers = { GER ENG }
	}
}
```

- `province_max` set = provincial building (per-province `show_on_map`);
  otherwise state-level. CLAIM(buildings-fields)
- Modifier blocks split by scope: `country_modifiers` accept only country
  modifiers, `state_modifiers` only state modifiers; `enable_for_controllers`
  restricts by controller list. CLAIM(buildings-modifier-split)

## Start bookmarks (`common/bookmarks/*.txt`)

The scenario cards on the title screen. Vanilla ships exactly two —
`the_gathering_storm.txt` (1936) and `blitzkrieg.txt` (1939); mods add
their own file and it appears as an extra card.

```txt
bookmarks = {
	bookmark = {
		name = "GATHERING_STORM_NAME"    # loc keys
		desc = "GATHERING_STORM_DESC"
		date = 1936.1.1.12               # FOUR parts — hour included
		picture = "GFX_select_date_1936"
		default_country = "GER"
		default = yes

		filters = { new_content continent }  # a 'label' filter adds a button

		"FRA" = {
			history = "FRA_GATHERING_STORM_DESC"
			ideology = democratic
			version = base_game
			available = { NOT = { has_dlc = "La Resistance" } }
			ideas = { FRA_victors_of_wwi }
			focuses = { FRA_form_the_popular_front }
		}
	}
}
```

- Vanilla `date` uses four parts — year.month.day.**hour**; keep the
  format vanilla uses. CLAIM(bookmark-four-part-date)
- A country may appear multiple times: one entry per DLC `version`
  (`base_game` vs e.g. `la_resistance`, gated by `available` /
  `required_dlc`) — the game picks by installed DLC and shows different
  starting ideas/focuses per version. CLAIM(bookmark-dlc-versions)

## Difficulty settings (`common/difficulty_settings/00_difficulty.txt`)

The per-country toggles of the "custom difficulty" mode:

```txt
difficulty_settings = {
	difficulty_setting = {
		key = "custom_diff_strong_ger"
		modifier = diff_strong_ai_generic  # a STATIC modifier, defined in
		                                   # common/modifiers/00_static_modifiers.txt
		countries = { GER }
		multiplier = 2.0
	}
}
```

`multiplier` scales the referenced static modifier when the player
enables the toggle for that country. CLAIM(difficulty-setting-multiplier)

## Scripted map modes (`common/map_modes/`)

The one `common/` system that ships its own authoritative doc — read
`common/map_modes/documentation.md` in the game install first. Scripted
map modes add map-mode buttons: loc keys derive from the mode name
(`MAPMODE_<name>[_NAME|_DESCRIPTION]`, `<name>_tooltip[_delayed]`) and
icons are `GFX_mapmode_buttons_(de)selected_small_<name>`:

```txt
scripted_map_modes = {
	test_map_mode = {
		top = {
			type = country   # or state, state_controller, none — or a
			                 # hardcoded game_map_mode_* layer (then all
			                 # other layer entries are ignored)
			color = {
				# scope: player; from: the rendered country/state
				set_temp_variable = { red = 0.0 }
				set_temp_variable = { blue = 1.0 }
				set_temp_variable = { green = 0.0 }
				set_temp_variable = { alpha = 1.0 }
				# set_temp_variable = { thickness = 10.0 }   # only if parent has thickness = yes
				# set_temp_variable = { highlighted = 1.0 }  # pulsating border
			}
		}
		# bottom = { ... } renders beneath top
	}
}
```

- Border colors come from temp variables the `color` trigger sets — the
  game reads red/blue/green/alpha (0.0–1.0) when the trigger returns
  true. CLAIM(map-mode-color-temps)

## Name pools (`common/names/00_names.txt`)

One self-documented 9.5k-line vanilla file feeding random generation for
ACES and OPERATION order names. `default` holds the generic pools;
per-country blocks (`GER = { ... }`, `ENG = { ... }`, ...) override it:

```txt
default = {
	male = {
		names = { "John" "Bob" ... }
		surnames = { }
		callsigns = { }
	}
	surnames = { "Smith" "Jones" ... }
	callsigns = { "Easy Kill" ... }
	# female = { ... } is optional
}
```

- Aces draw name + surname (the combination never repeats) plus at most
  one callsign; a used callsign is never assigned again.
  CLAIM(ace-name-uniqueness)
- Operation names: pools can be narrowed per strategic region; the
  historical sub-pool is preferred while it lasts (exhaustion governed by
  the `HISTORICAL_ORDER_NAME_EXHAUSTION` define; region index 0 is the
  generic national pool), then a first/second pair is drawn from the
  default pool. The prefix must exist in every pool.
  CLAIM(operation-name-pools)

## Verification

1. Validator; 2. game rules visible on the rules screen; ideologies in
   politics view; buildings in the construction tab and on map; bookmark
   card on the title screen; difficulty toggles under custom difficulty;
   custom map mode button in-game; generated ace/operation names; 3.
   triage.
