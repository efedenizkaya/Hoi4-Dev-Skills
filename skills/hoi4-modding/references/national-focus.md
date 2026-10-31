# National focus trees

Focus trees live in `<mod>/common/national_focus/<tag or name>.txt`. A mod
replaces a country's tree by giving the country a tree with
`shared_focus`-style top block: `focus_tree = { id = ... country = { factor
= ... } }` — a country uses the tree whose `country` weight picks it; a mod
tree with the country's tag in its id and `country = { factor = 100 }`
overrides vanilla for that country when loaded after (see
[mod-structure.md](mod-structure.md) for load order).

CLAIM(focus-tree-placement)

## Anatomy

```txt
focus_tree = {
	id = mymod_germany_tree
	default = no                       # not the fallback tree for everyone
	country = {
		factor = 0                      # vanilla pattern: base 0, add per tag
		factor = 0                      # vanilla pattern: base 0, add per tag
		                                   CLAIM(focus-tree-selection)
		modifier = { add = 10 tag = GER }
	}


	focus = {
		id = mymod_rearm
		icon = GFX_focus_generic_industry
		x = 5                          # grid position, see below
		y = 0                          # row (0 = first row); x is the column
		cost = 5                       # in POINTS; define FOCUS_POINT_DAYS = 7,
		                               # so 1 point = 1 week of progress
		                               CLAIM(focus-cost-weeks)
		available = { has_idea = mymod_mobilization }   # can it START
		bypass = { has_war_with = POL }                 # auto-complete condition
		mutually_exclusive = { focus = mymod_alt_path }
		prerequisite = { focus = mymod_rearm_2 }        # AND groups:
		prerequisite = { focus = mymod_a focus = mymod_b }  # a OR b
		completion_reward = {
			add_ideas = mymod_rearm_idea
		}
		ai_will_do = { factor = 10 }   # AI pick weight
		search_filters = { FOCUS_FILTER_POLITICAL }
	}
}
```

CLAIM(focus-fields)

## Positioning rules

- `x`/`y` are grid coordinates on the tree; `y = 0` is the 1936 column.
  Overlapping same-row focuses need distinct x.
- `relative_position_id = <focus id>` makes x/y relative to that focus —
  the standard way to keep branches together when inserting focuses later.
  CLAIM(relative-position)
- Focuses visible from the start need no `prerequisite`; deeper ones must
  chain. A focus with no path from y=0 is unreachable in the UI.

## Common bugs (from real mod triage)

- **Duplicate focus id** across files silently breaks the tree — vanilla ids
  included (`GER_four_year_plan` etc. are taken). The validator checks
  *event* duplicate ids; focus-id uniqueness is not checked — grep your
  tree before finishing. CLAIM(focus-dup-silent)
- `mutually_exclusive` must be declared on **both** focuses — vanilla
  `germany.txt` declares each pair from both sides (99 occurrences, every
  pair bidirectional). CLAIM(mutual-exclusive-both)
- `available` blocks starting; `bypass` auto-completes. Confusing them makes
  branches permanently locked.
- Reward effects run in the **country scope of the tree owner**; effects
  needing a state/character scope must re-scope explicitly.

## AI weights

`ai_will_do` unset behaves like a low default weight (verify exact value
against vanilla trees before relying on it). Use `modifier = { factor = ... }`
blocks inside for conditions. Weights are relative within the same branch
layer. CLAIM(ai-will-do-default) `[unverified]`

## Worked example

No focus kit is shipped yet. For the file-set pattern (script + loc +
verification), see [../assets/kits/decision-kit/](../assets/kits/decision-kit/MANIFEST).

## Verification steps

1. `python tools/validate.py <mod_dir>` — event-id duplicates, balance,
   focus prerequisite/exclusivity/overlap rules.
2. In-game: console (needs `-debug`) has `Focus.AutoComplete`,
   `Focus.IgnorePrerequisites`, `Focus.NoChecks` for tree testing; then
   `python tools/error_triage.py logs/error.log` — look for
   `invalid-database-object` and `invalid-scope` classes.
3. Visual check: tree renders, branches lock correctly, no orphan branches.

## Complete focus field reference (vanilla census, 1.19.4.1)

Frequency across all vanilla `common/national_focus/*.txt`:

| Field | Freq | Notes |
|---|---|---|
| `prerequisite` | 11268 | AND groups; `{ focus = a focus = b }` = OR inside |
| `cost`, `id`, `icon`, `x`, `y` | ~10676 | |
| `completion_reward` | 10676 | effects in owner country scope |
| `relative_position_id` | 10473 | x/y relative to another focus |
| `available` | 10063 | can it START |
| `search_filters` | 9225 | `FOCUS_FILTER_*` tokens |
| `ai_will_do` | 7391 | |
| `bypass` | 6160 | auto-complete condition |
| `available_if_capitulated` | 5734 | |
| `cancel_if_invalid` / `continue_if_invalid` | ~4000 | invalid-handling pair |
| `mutually_exclusive` | 2759 | both sides (see above) |
| `will_lead_to_war_with = TAG` | 786 | flags war intent to the AI/target |
| `offset` | 737 | |
| `allow_branch` | 543 | trigger gating a whole branch |
| `complete_tooltip` | 374 | |
| `dynamic = yes` (tree-level) | 153 | tree re-evaluated (formable nations) |
| `select_effect`, `overlay`, `text_icon`, `enable_automatic_bypass`, `alternate_icon`, `cancel`, `bypass_effect`, `historical_ai` | rare | |

Tree-level fields: `default`, `country` (factor pattern), `dynamic`,
`continuous_focus_position`, plus `shared_focus`/`joint_focus` headers for
shared trees. CLAIM(focus-census)
