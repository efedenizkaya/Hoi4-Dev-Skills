# Peace conference

Structure: `common/peace_conference/{categories,cost_modifiers,ai_peace}/`.
The peace ACTIONS (take_states, puppet, force_government, liberate) are
engine-defined; mods script **categories** (UX grouping) and **cost
modifiers**. The game ships its own doc at
`common/peace_conference/cost_modifiers/_documentation.md`.

CLAIM(pc-files)

## Scope contract (the key to this system)

From the game's own documentation:

- `ROOT` — negotiator country (who is negotiating)
- `FROM` — taker country (owner after the conference)
- `FROM.FROM` — giver country (owner before)
- `FROM.FROM.FROM` — the state, when the action targets one

CLAIM(pc-scope-contract)

## Cost modifiers

```txt
peace_action_modifiers = {
	generic_is_core = {
		category = is_core               # UX grouping; same category = one number
		peace_action_type = take_states  # or an array: { puppet liberate }
		enable = {                       # any trigger; prefer pc_* triggers
			FROM.FROM.FROM = { is_core_of = ROOT.FROM }
		}
		cost_multiplier = 0.65           # must be > 0
	}
}
```

- **All active modifiers multiply together** — the game's doc says stay
  near 1.0 (roughly 0.4–3.0); extremes behave badly.
  CLAIM(pc-multiplied-costs)
- Conference-time state changes are NOT live in `enable`: use the
  `pc_*` triggers (e.g. `pc_is_puppeted_by`) for things happening during
  the conference — ordinary ownership/diplomacy triggers read pre- or
  post-conference state. CLAIM(pc-triggers-live)

## Categories

`common/peace_conference/categories/*.txt`:

```txt
peace_action_categories = {
	other = { default = yes name = PEACE_ACTION_CATEGORY_OTHER }  # one default
	occupation = { name = PEACE_ACTION_CATEGORY_OCCUPATION }
	ideology = { name = PEACE_ACTION_CATEGORY_IDEOLOGY }
	...
}
```

## AI peace

`ai_peace/` scores actions for the AI (`_documentation.md` in the folder).

## Verification

1. Validator (scoping like `FROM.FROM.FROM` is brace-dense).
2. In game: win a war → conference screen; category grouping and costs
   visible in tooltips.
3. Triage: `invalid-scope` for broken FROM chains.

## AI peace desires (`ai_peace/`)

Same scope contract, opposite knob — **desires affect AI behavior, not
cost**:

```txt
peace_ai_desires = {
	arbitrary_name_for_the_desire = {
		peace_action_type = force_government   # single or array
		enable = { ... }                       # same pc_* trigger caveat
		ai_desire = 100    # PERCENT: +100 = double desire, 0 = no change,
		                   # -50 = halve; <= 0 total = AI won't take it
	}
}
```

- Active desires are **SUMMED** (cost modifiers multiply — don't mix the
  two mental models). CLAIM(pc-ai-desires-summed)
- `ai_desire` is a percentage modifier, not a weight. CLAIM(pc-ai-desire-percent)
