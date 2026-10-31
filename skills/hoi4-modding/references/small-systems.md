# Small systems: game rules, ideologies, buildings

Three single-file systems, each small enough to master in minutes.

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

## Verification

1. Validator; 2. game rules visible on the rules screen; ideologies in
   politics view; buildings in the construction tab and on map; 3. triage.
