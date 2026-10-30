# Ideas, national spirits and modifiers

Three related systems, three file locations:

| System | File | What it is |
|---|---|---|
| Ideas / national spirits | `common/ideas/*.txt` | country-level effects: laws, designers, spirits, advisors' tokens |
| Static modifiers | `common/modifiers/*.txt` (`00_static_modifiers.txt`) | engine-named bundles applied by game features (weather, power balance); names are code-referenced, never remove them |
| Custom modifier types | `common/modifier_definitions/*.txt` | declarations a custom modifier type needs before static modifiers can use it |
| Dynamic modifiers | `common/dynamic_modifiers/*.txt` | variable-driven modifier bundles applied via `add_dynamic_modifier` |

CLAIM(static-modifier-paths)

CLAIM(ideas-file-map)

## Idea structure

Ideas are grouped in **categories**, defined in `common/idea_tags/*.txt`:

```txt
idea_categories = {
	hidden_ideas = { hidden = yes cost = 0 removal_cost = -1 ledger = hidden }
	country = { type = national_spirit ... }
	mobilization_laws = { ... }
	...
}
```

Each category (idea slot) controls cost, ledger placement and whether it
shows in the politics view. `type = national_spirit` makes the category a
spirit list. CLAIM(idea-categories)

An idea body (vanilla `war_economy`, `common/ideas/_economic.txt`):

```txt
war_economy = {
	available = { has_war_support > 0.5 ... }   # can be taken (law upgrade)
	allowed = { ... }                            # can exist at all (tags, dlc)
	cancel_if_invalid = no                       # stay when conditions lapse
	modifier = {
		consumer_goods_expected_value = 0.2
		production_speed_arms_factory_factor = 0.2
	}
	on_add = { ... }    # effects on gaining; on_remove also exists
}
```

Laws upgrade by `add_ideas = war_economy` replacing the slot's current idea.
Cost/removal_cost come from the **category**, overridable per idea (comment
in vanilla `00_idea.txt`: idea > idea slot > category, first wins).

CLAIM(idea-body-fields)

## Using ideas from script

- `add_ideas = <idea>` / `remove_ideas = <idea>` (country scope; both exist
  in 1.19.4.1 effects — verified via effects.json).
- Check with `has_idea = <idea>` (trigger).
- Timed ideas: `add_timed_idea = { idea = <idea> days = 180 }` — check the
  exact field set in effects.json for your version before using extras like
  `mins`.

CLAIM(idea-script-effects)

## Dynamic modifiers

The game documents its own pattern in `common/dynamic_modifiers/
0_dynamic_modifiers.txt`:

```txt
# definition
mymod_bonus = {
	icon = "GFX_idea_unknown"          # optional
	enable = { always = yes }          # optional gate
	remove_trigger = { always = no }   # optional auto-removal
	production_speed_arms_factory_factor = 0.1
	max_fuel = var_max_fuel            # values can be variables
}

# application (country or state scope)
add_dynamic_modifier = {
	modifier = mymod_bonus
	scope = GER      # optional: binds the modifier to that scope
	days = 14        # optional: auto-expiry
}
```

Values may be plain numbers or variables — that is what makes them
"dynamic" (e.g. scaling with war support). Check `has_dynamic_modifier`
(trigger) to test presence. CLAIM(dynamic-modifier-syntax)

## Modifier names

Valid modifier names for the current patch are in
`extracted/<version>/modifiers.json` (scope → names; templated names like
`<Building>_output` are patterns, e.g. `arms_factory_output`). Picking a
name from an older patch is a classic silent-no-op bug: the game ignores
unknown modifiers **without an error** — validate the exact name exists in
the scope you apply it to. CLAIM(unknown-modifier-silent) `[unverified]`

## Verification steps

1. Validator: idea tokens referenced by events/decisions must exist
   (missing-loc-key catches their text).
2. Game run: `setup.log` lists loaded ideas per file (`Ideas loaded
   'common/ideas/...' ideas #N`) — a file that fails to parse drops out
   of that list. CLAIM(setup-log-idea-counts)
3. In-game politics view shows spirits/laws; ledger placement wrong =
   category `ledger` misconfigured.
