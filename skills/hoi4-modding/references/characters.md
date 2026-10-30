# Characters

Since 1.16 characters are the single system behind leaders, advisors and
commanders. Files: `common/characters/<TAG>.txt` (one block per character),
`history/countries/<TAG> - Country.txt` assigns starting ones via
`recruit_character = <token>`.

CLAIM(character-files)

## Structure

```txt
characters = {
	GER_my_leader = {
		name = GER_my_leader            # loc key OR literal string
		portraits = {
			civilian = { large = GFX_portrait_my_leader_civ }
			army = { large = GFX_portrait_my_leader_army small = GFX_portrait_my_leader_small }
		}

		country_leader = {              # role: head of state
			ideology = stalinism        # subtype of the country's ideology
			expire = "1950.1.1.1"
			traits = { inspiring_orator }
		}

		advisor = {                     # role: political/military advisor
			slot = political_advisor
			idea_token = GER_my_leader_advisor   # REQUIRED: the idea used in ledgers
			allowed = { original_tag = GER }
			visible = { ... }
			available = { ... }
		}

		corps_commander = {             # role: land commander
			traits = { trait_cautious brilliant_strategist }
			skill = 4
			attack_skill = 4
			defense_skill = 3
			planning_skill = 4
			logistics_skill = 2
		}

		field_marshal = { ... }         # role: field marshal
		navy_leader = { ... }           # role: naval commander
		scientist = { ... }             # role: special projects scientist
	}
}
```

CLAIM(character-roles)

- `name` may be a literal string or a localisation key — vanilla uses both;
  the loc key version is translatable.
- One character, many roles: the advisor `idea_token` is how the same
  character appears in the political ledger.
- Portrait families: `civilian` / `army` / `navy`; `large` required,
  `small` optional (defaults to large). CLAIM(portrait-families)

## Script surface (all verified in 1.19.4.1)

- Effects: `recruit_character`, `add_advisor_role`, `add_corps_commander_role`,
  `add_country_leader_role`, `add_field_marshal_role`,
  `add_unit_leader_trait`, `set_character_flag` …
- Triggers: `has_character_flag`, `has_trait`, `is_character` …
- Scope: a character token used bare (`GER_my_leader`) resolves only if the
  character was **recruited/assigned to the current scope's country**; the
  game logs `tried to use character X as scope, but could not find this
  character in country Y` otherwise (real error.log class). CLAIM(character-scope-rule)

## Common bugs

- History files: `recruit_character` before anything that scopes the
  character (flags, unit assignment) — same-file ordering matters.
- One character assigned to two countries at once: the game rejects with
  `cannot be assigned to X as it is already assigned to Y` — give the
  character two entries or use `add_corps_commander_role` with care.
  CLAIM(character-already-assigned)
- Missing `idea_token` on an advisor = invisible in the ledger.

## Verification steps

1. `python tools/validate.py <mod_dir>` (loc keys of names).
2. Launch → `python tools/error_triage.py logs/error.log` — character
   classes: `invalid-scope`, "cannot be assigned", "could not find this
   character".
3. In game: politics view for leaders/advisors; leader list for commanders.
