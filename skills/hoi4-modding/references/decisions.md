# Decisions and decision categories

Files: `common/decisions/categories/*.txt` for categories (flat blocks),
`common/decisions/*.txt` for the decisions themselves. Decisions may live
flat in the file or nested inside their category block — vanilla uses both
patterns (e.g. `fascism_on_the_rise` nests its decisions). CLAIM(decision-placement)

## Category

```txt
mymod_category = {
	icon = generic_political_actions   # icon token, not a GFX sprite

	allowed = { ... }    # which countries get the category at all
	visible = { ... }    # when the tab shows
}
```

## Decision body

```txt
mymod_boost_morale = {
	icon = generic_national_unity

	available = { has_war = yes }       # can be taken now
	visible  = { has_war = yes }        # shows in the list
	activation = { ... }                # optional: auto-activates when true
	                                     # (for crisis-style decisions)

	cost = 50                            # POLITICAL POWER by default;
	days_remove = 14                     # delayed effect phase
	days_re_enable = 30                  # cooldown after completion
	fire_only_once = yes                 # one-shot
	cancel_if_not_visible = yes          # disappears if visible fails mid-run

	complete_effect = { ... }            # on click
	remove_effect = { ... }              # after days_remove
	timeout_effect = { ... }             # if an activated one expires
	modifier = { ... }                   # active while in progress

	targeted_modifier = { tag = FRA ... }   # affects another country
	target_root_trigger = { ... }           # which targets are valid

	ai_will_do = { factor = 5 }
}
```

CLAIM(decision-fields)

## Gotchas (from real triage)

- `available` vs `visible` confusion: invisible decisions that are
  available do nothing visible; the reverse silently misleads the player.
- `cost` is **political power** by default. Command-power decisions use
  `custom_cost_trigger = { command_power > N }` plus
  `custom_cost_text = <loc key>` instead (vanilla BEL.txt pattern).
  CLAIM(decision-cost-political-power)
- One-shot decisions need `fire_only_once = yes`; without it they come back
  after `days_re_enable` (default 0 → immediately repeatable).
- Effects in `complete_effect` run in **country scope**; targeted decisions
  run with `FROM` = target.

## Worked example

[../assets/kits/decision-kit/](../assets/kits/decision-kit/MANIFEST) — a
complete, validator-clean category + two decisions with localisation.

## Verification steps

1. `python tools/validate.py <mod_dir>`.
2. In game: decisions tab shows the category (`visible` chain holds);
   console `pp` gives command power for testing cost.
3. error.log triage — decision parse failures surface as
   `invalid-database-object` / missing-loc classes.
