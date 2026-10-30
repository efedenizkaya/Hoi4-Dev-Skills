# Control flow, scope iteration and event targets

The heart of HOI4 scripting is moving between scopes correctly. This page
covers the constructs; per-effect scopes live in the extracted JSON.

## if / else_if / else — with limit

`if` is an EFFECT; its condition lives in the `limit` TRIGGER block:

```txt
if = {
	limit = { has_war_support > 0.5 }      # trigger grammar here
	add_war_support = 0.1                  # effect grammar here
}
else_if = {
	limit = { ... }
	...
}
else = { ... }
```

An `if` with no matching `limit` entry evaluates as false. CLAIM(if-limit)

## Scope iteration — every_ / random_ / any_

Three families, different grammars:

```txt
# every_* / random_* are EFFECTS: they change scope and run effects
every_country = { limit = { has_idea = mymod_idea } add_political_power = 10 }
random_owned_state = { add_building_construction = { ... } }

# any_* are TRIGGERS: they test a condition, inside limit blocks
any_other_country = { has_war_with = ROOT }
```

Mixing these up is the classic "it does nothing / it errors" bug: `any_*`
inside an effect block, or `every_*` inside a trigger, is wrong. The
per-version lists are in `triggers.json`/`effects.json`. CLAIM(iteration-families)

## random_list

```txt
random_list = {
	50 = { add_political_power = 100 }
	30 = { add_war_support = 0.05 }
	20 = { country_event = { id = mymod.7 } }
}
```

Weights are relative. A missing weight entry defaults to 0 (never picked).

## Event targets

Named scopes that survive across effect blocks and events:

```txt
FROM = { save_event_target_as = alliance_inviter }
event_target:alliance_inviter = { ... }        # read it back later
save_global_event_target_as = mymod_big_bad    # survives globally
clear_global_event_target = mymod_big_bad
```

Local targets live for the current effect chain; global targets persist —
always clear globals when done or they leak across sessions. CLAIM(event-targets)

## for_each_loop / while loops

```txt
for_each_loop = { array = mymod_targets ... }
while_loop = { limit = { check_variable = { mymod_i < 10 } } ... }
```

Loops are unbounded — a wrong limit condition freezes the game; prefer
bounded `for_each_*` forms. Verify the exact field names against the
game's `documentation/script_concept_documentation.md` for the installed
patch. CLAIM(loops)

## The § and £ sanity note

`§` (colors) and `£` (icons) belong in LOCALISATION, never in script
files; seeing them in a .txt is a copy-paste from a wiki or loc file.

## Verification

1. `scripts/validate.py` — brace balance is the #1 control-flow killer.
2. `--data` statement check catches `any_*` used as an effect.
3. Game run + `error_triage` — scope errors surface as `invalid-scope`.
