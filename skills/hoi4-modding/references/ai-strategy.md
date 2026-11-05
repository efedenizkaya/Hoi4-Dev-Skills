# AI strategy

Files: `common/ai_strategy/*.txt` (conditional strategy blocks),
`common/ai_strategy_plans/*.txt` (named plans grouping strategies),
`common/ai_templates/*.txt` (unit templates), `common/ai_schemes/`
(operation schemes).

## Strategy block

```txt
ARG_avoid_china = {
	allowed = {                      # country gate (original_tag, has_dlc)
		original_tag = CHI
	}
	enable = {                       # when the strategy is active
		is_historical_focus_on = yes
	}
	abort = { date > 1945.1.1 }      # optional stop condition

	ai_strategy = {
		type = alliance
		id = "ARG"                   # target (tag / area / archetype…)
		value = -1000                # magnitude, sign = direction
	}
}
```

CLAIM(ai-strategy-block)

## Strategy `type` values actually used in vanilla 1.19.4

Top of the frequency list (grep over `common/ai_strategy/*.txt`):
`role_ratio` (315), `unit_ratio` (209), `template_prio` (142),
`alliance` (128), `equipment_production_factor` (103), `area_priority`
(103), `befriend` (86), `put_unit_buffers` (81), `research_weight_factor`
(79), `front_unit_request` (79), `antagonize` (74), `diplo_action_desire`
(69) — and more. Prefer copying the nearest vanilla usage of a type over
guessing its `id`/`value` semantics; types differ in what `id` means.

CLAIM(ai-strategy-types)

## Plans

`ai_strategy_plans/<name>_strategy_plan.txt`:

```txt
German_historical = {
	name = "German historical plan"
	desc = "..."
	allowed = { original_tag = GER }
	enable = {
		is_historical_focus_on = yes
		OR = { ... }               # often gated by has_game_rule
	}
	# strategies referenced from here apply while the plan is enabled
}
```

Plans + game rules (`has_game_rule`) is how vanilla switches AI behavior
sets (historical vs alt-history). CLAIM(ai-plans-game-rules)

## Unit templates

`common/ai_templates/*.txt` name template patterns the AI builds; the AI
then uses `template_prio`/`unit_ratio` strategies to apply them.

## Debugging AI

`logs/ai.log` and `ai_trace.log` record AI activity; `-debug` mode adds
more. Balance-of-behavior bugs are rarely single-line: bisect by disabling
your strategy blocks (`allowed = { always = no }`) until the behavior
changes. CLAIM(ai-debug-logs)

## Verification steps

1. Validator (braces/quotes; strategy files are big and brace-heavy).
2. error.log triage after a run.
3. Behavior test: observer game (`debug_always_ready`/observer) watching
   the targeted country, or `ai.log` grep for the country tag.

## AI focus preferences (`common/ai_focuses/*.txt`)

How the AI weights research while pursuing a focus-branch persona:

```txt
ai_focus_defense_ENG = {
	research = {
		defensive = 5.0
		radar_tech = 1.0
		construction_tech = 2.0
	}
}
```

`research` maps technology categories to weights. The file name is free
form. Which branches the AI actually picks is driven by the focuses'
`ai_will_do` plus game rules — see the tree side in
[national-focus.md](national-focus.md). CLAIM(ai-focuses)
