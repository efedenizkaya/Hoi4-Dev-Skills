# Military industrial organizations (MIO)

MIOs replaced design companies (Arms Against Tyranny DLC). The **game ships
its own authoritative documentation** at
`common/military_industrial_organization/organizations/_documentation.md` —
read it for the full field list; this page is the distilled workflow.

Files:

```
common/military_industrial_organization/
├── organizations/     # the MIO definitions (+ _documentation.md, _template_organization.txt)
├── policies/          # assignee policies (+ per-domain _documentation.md)
└── ai_bonus_weights/  # AI pick weights
```

CLAIM(mio-files)

## Minimal MIO

```txt
mymod_tank_mio = {
	allowed = { original_tag = GER }     # MANDATORY — instance created per country
	visible = { ... }                    # FROM = country; default always
	available = { ... }                  # greyed-out when false

	equipment_type = {                   # archetypes/categories matched to variants
		cat_anti_tank_equipment          # see script_enum_equipment_bonus_type
	}                                    # and common/equipment_groups
	research_categories = { infantry_weapons }

	research_bonus = 0.2                 # defaults from defines otherwise
	task_capacity = 3

	trait = {
		token = mymod_upgrade_1          # mandatory; loc falls back:
		                                 # TAG_<token> → <token>
		parent = { traits = { ... } num_parents_needed = 1 }
		equipment_bonus = { ... }
		production_bonus = { ... }
		organization_modifier = { ... }
	}
}
```

CLAIM(mio-minimal)

## Key mechanics (from the game's own doc)

- `allowed` is evaluated **at game start for every country**; keep it cheap
  and tag-based. CLAIM(mio-allowed-at-start)
- Trait trees: `parent` (with `num_parents_needed`), `any_parent`,
  `all_parents`; mutual exclusivity must be set on both traits.
- Naming fallback chain for loc and icons: `GFX_TAG_<token>` →
  `GFX_<token>` → `GFX_idea_unknown`. CLAIM(mio-loc-fallback)
- on-actions (`on_design_team_assigned_to_tech`, …) run with MIO scope,
  `FROM` = country.
- `ai_will_do` multiplies the weights in `ai_bonus_weights/`.

## DLC gating

MIO content requires `allowed = { has_dlc = "Arms Against Tyranny" }` —
vanilla wraps every MIO in it. Without the gate, non-DLC players hit
undefined content. CLAIM(mio-dlc-gate)

## Verification steps

1. `python tools/validate.py <mod_dir>`.
2. `setup.log`/`error.log` after a run — MIO parse errors are loud.
3. In game: company list in the production/research tabs; assign to a tech
   and a variant to exercise both on-actions.

## Policies (`policies/` — game-shipped `_documentation.md`)

One policy can be attached per MIO for extra bonuses, scoped to the
assigned equipment variant or production line. Fields mirror traits
(name fallback chain, optional icon, `allowed`/`available` triggers with
FROM = country). CLAIM(mio-policies)
