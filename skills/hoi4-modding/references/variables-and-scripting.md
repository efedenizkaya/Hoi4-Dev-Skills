# Variables and scripting

The game ships authoritative per-version docs inside the install — read
them via the extractor or directly; do not trust older wiki pages:

| Doc file | Contents |
|---|---|
| `documentation/dynamic_variables_documentation.md` | read-only dynamic variables per scope (country/state/unit_leader/MIO/special_project/global) |
| `documentation/script_concept_documentation.md` | core scripting concepts |
| `documentation/script_math_functions.md` | `add`, `multiply`, `clamp`, `cos`, … usable inside values |
| `documentation/script_collection_input.md` / `_operator.md` | collections: `controlled_states`, `faction_members`, `country_and_all_subjects`, … |
| `documentation/console_commands_documentation.md` | console commands |

CLAIM(script-doc-files)

## Variable basics

```txt
set_variable = { mymod_strength = 5 }
add_to_variable = { mymod_strength = 1 }
multiply_variable = { mymod_strength = 2 }
subtract_from_variable = { mymod_strength = 1 }
set_temp_variable = { tmp = mymod_strength }     # temp: gone after current effect chain
```

- Variables live **per scope** (country, state, global). Reading an unset
  variable yields 0 — silence is the trap; typos produce 0, not errors.
  CLAIM(unset-var-zero)
- Values in effects/triggers that accept variables take them via `var:` —
  using a bare name reads the **database object** of that name instead.
  The game's error for getting this wrong:
  `invalid database object for effect/trigger: X. use var:var_name ...`
  CLAIM(var-prefix)
- `@alias` at file top defines constants: `@my_cost = 50`, used as
  `@my_cost`.

## Arrays and flags

```txt
add_to_array = { mymod_targets = GER }           # array per scope
add_to_array = { mymod_targets = global.GER }    # store another scope
remove_from_array = { mymod_targets = GER }
clear_array = mymod_targets
any_of = { array = mymod_targets ... }           # iterate (check doc for
                                                 # every/any/all variants)
set_country_flag = mymod_flag                    # flags: no value, check-only
set_country_flag = { flag = mymod_flag days = 30 value = 1 }
```

Flags vs variables: use flags for "happened yes/no" (with optional expiry),
variables for numbers. Array/scoped storage (`global.` prefix) is how you
keep cross-country data. CLAIM(flags-vs-vars)

## Scripted effects/triggers

`common/scripted_effects/*.txt`, `common/scripted_triggers/*.txt` — named
reusable blocks:

```txt
mymod_prepare_for_war_effect = {
	add_war_support = 0.1
	army_experience = 20
}
# usage inside any effect block:
mymod_prepare_for_war_effect = yes
```

Arguments are passed by setting variables before the call — HOI4 has **no
effect parameter syntax** (`my_effect = { ARG = 5 }` / `$ARG$` is
CK3/Stellaris, not HOI4; vanilla `common/scripted_effects/` contains no
`$`).
  CLAIM(scripted-effect-no-params) Prefix names with your mod tag to avoid collisions, and
keep one file per domain. CLAIM(scripted-effect-args) `[unverified]`

## on_actions

`common/on_actions/*.txt` hooks game events:

```txt
on_actions = {
	on_weekly = { effect = { mymod_weekly_tick_effect = yes } }
	on_declare_war = { effect = { ... } }
}
```

Check the full hook list in the game's `documentation/` or vanilla
`common/on_actions/00_on_actions.txt` before inventing hook names — a
misspelled hook silently never fires. CLAIM(on-actions-silent)

## Math and collections

Inside any value position you can use script math functions
(`clamp(x, min, max)`, `add`, `divide`, …) and collections
(`controlled_states^num` for counts, `^` indexing). The doc files above are
generated per patch — prefer them over memorized lists.

## Script constants and enums (`common/script_constants/`, `common/script_enums.txt`)

Reusable script values defined once and referenced from any scoped
variable context via the `constant:` prefix. The game ships its own
authoritative doc — `common/script_constants/documentation.md` in the
install — read it before inventing schemas.

```txt
# common/script_constants/country_groups.txt (vanilla) — a constant of
# country-typed array data:
country_groups = {
	schema = {
		any_key = yes
		array = country
	}
	nordics = { SWE NOR FIN DEN ICE }
}

# usage in script:
any_of = { array = constant:country_groups.nordics ... }
```

- Constant entries carry a `schema` block — `key = <name>` or
  `any_key = yes`, then `data = int | fixed_point | { complex schema }`.
  Vanilla examples: `country_groups`/`state_groups` (country/state
  arrays), `sp_complexity` (min/max ints). CLAIM(script-constant-schema)
- Access uses the `constant:` prefix (e.g.
  `constant:country_groups.nordics`); only entries documented to support
  constants can use them. CLAIM(script-constant-prefix)
- Reload gotcha straight from the game's own doc: reloading the script
  database is NOT enough to propagate constant changes — the script that
  consumes them must be reloaded too. CLAIM(constant-reload-caveat)
- `common/script_enums.txt` defines `script_enum_<name> = { value ... }`
  lists (operative mission types, advisor slot types, equipment stats)
  usable wherever a parameter expects that enum. Vanilla comments warn
  which equipment stats MIOs actually honor.
  CLAIM(script-enums-files)

## Verification steps

1. Static lint (braces/quotes balance — variable code is brace-dense).
2. Use the `log` effect or console `dump_data`-style commands to print
   variable values while testing; remove before release.
3. error.log triage: `invalid-database-object` class = var: misuse.
