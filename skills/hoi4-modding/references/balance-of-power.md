# Balance of Power (BoP)

Sliding-scale political mechanic (1.14+). Files: `common/bop/<tag or
name>.txt`. One file may hold several balances. Vanilla ships 9 country
files plus `_test.txt` (a syntax cheat-sheet worth reading).

CLAIM(bop-files)

## Anatomy

```txt
BRA_political_military_balance = {
	initial_value = -0.0
	left_side = BRA_bop_left_side        # side ids defined below
	right_side = BRA_bop_right_side
	decision_category = BRA_balance_of_power_category   # where the UI lives

	range = {
		id = BRA_unstable_government     # a neutral middle band
		min = -0.1
		max = 0.1
		modifier = { ... }               # static modifiers active in this band
		on_activate = { ... }            # effects when the band is entered
		on_deactivate = { ... }
	}

	side = {
		id = BRA_bop_left_side
		icon = GFX_bop_ETH_communist_side
		range = { id = ... min = -1 max = -0.1 modifier = { ... } }
	}
	side = {
		id = BRA_bop_right_side
		icon = GFX_bop_ETH_fascist_side
		range = { id = ... min = 0.1 max = 1 modifier = { ... } }
	}
}
```

CLAIM(bop-anatomy)

## Rules that bite

- Value domain is **-1 to +1**; `min`/`max` bands must not overlap or the
  active band is ambiguous.
- Band `modifier` blocks hold STATIC modifiers (`common/modifiers/`), not
  direct effects. CLAIM(bop-static-modifiers)
- Sides without `icon` break the UI rendering.
- The UI needs the `decision_category` to exist (see
  [decisions.md](decisions.md)).

## Script surface (all verified in 1.19.4.1)

- Effects: `add_power_balance_value`, `set_power_balance`,
  `add_power_balance_modifier` (id + `modifier = static_modifier_id`),
  `remove_power_balance_modifier`, `remove_all_power_balance_modifiers`,
  `remove_power_balance`, `set_power_balance_gfx`.
- Triggers: `has_power_balance`, `has_any_power_balance`,
  `is_power_balance_in_range`, `is_power_balance_side_active`,
  `power_balance_value`, `power_balance_daily_change`,
  `power_balance_weekly_change`, `has_power_balance_modifier`.

CLAIM(bop-script-surface)

## Verification

1. Validator (brace density is high).
2. In game: politics/decision tab shows the bar; drag happens via script
   (`add_power_balance_value`).
3. Triage: `invalid-database-object` for a bad static modifier id.
