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
		icon = GFX_focus_generic_industry_3
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

- `x`/`y` are grid coordinates on the tree: `x` = column, `y` = row
  (top row is 0). Neither relates to a year.
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

See [../assets/kits/focus-kit/](../assets/kits/focus-kit/MANIFEST) — a
validator-clean tree with mutual exclusion and a shared prerequisite.

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

## Complete search_filters census (vanilla 1.19.4.1)

Valid `FOCUS_FILTER_*` tokens with vanilla frequencies. **Generic** (safe
for any mod):

| Token | Freq | | Token | Freq |
|---|---|---|---|---|
| INDUSTRY | 2715 | | WAR_SUPPORT | 767 |
| POLITICAL | 2611 | | POLITICAL_CHARACTER | 441 |
| RESEARCH | 1767 | | MILITARY_CHARACTER | 294 |
| MANPOWER | 933 | | ARMY_XP | 278 |
| STABILITY | 911 | | BALANCE_OF_POWER | 226 |
| HISTORICAL | 870 | | AIR_XP | 191 |
| ANNEXATION | 845 | | NAVY_XP | 181 |
| INTERNATIONAL_TRADE | 93 | | INTERNAL_AFFAIRS | 88 |
| PROPAGANDA | 14 | | COMPLETED_BY_EVENT | 14 |

**DLC/country-specific** (only with that content): TFV_AUTONOMY,
IMPERIAL_INFLUENCE, SOV_POLITICAL_PARANOIA, INNER_CIRCLE, USA_CONGRESS,
SWI_MILITARY_READINESS, SPA_CIVIL_WAR (+ CARLIST/ANARCHIST_UPRISING),
TUR_KEMALISM/TRADITIONALISM/KURDISTAN, MEX_CHURCH_AUTHORITY/
CAUDILLO_REBELLION, CHI_INFLATION, GRE_DEBT_TO_IFC, ITA_MISSIOLINI,
MISSIOLINI, FRA_POLITICAL_VIOLENCE/OCCUPATION_COST, FOLKHEMMET.
Vanilla itself contains two typo tokens (`FOCUS_FILTER_INDUSTRIAL`,
`FOCUS_FILTER_BALANCE_OF_POWERS` — 1 use each) — copy from working
vanilla, not from other vanilla files blindly. CLAIM(focus-filter-census)

## shared_focus and joint_focus

Two real keywords for branches shared across countries (both verified in
vanilla): CLAIM(shared-vs-joint-focus)

- `shared_focus = { ... }` — one focus made available to every tree that
  includes the branch (vanilla: baltic_shared.txt 60, toa_shared 76,
  china_shared_TSR 69).
- `joint_focus = { ... }` — a focus JOINTLY owned by several countries at
  the same grid position; each country sees it (vanilla: ABDA 11,
  indonesia_joint 96, goe_shared_saadabad 18).

Both use the same focus fields. Positioning across trees relies on
`offset` blocks.

## offset — conditional pixel nudges, not grid

`offset = { x = -18 y = 0 trigger = { ... } }` shifts the focus by PIXELS
when the trigger holds (vanilla uses it to make obsolete branches slide
out of the way). It is not grid positioning and must not be read as x/y —
multiple offset blocks per focus are allowed. CLAIM(focus-offset-semantics)

`text_icon = <style>` picks a custom text-icon style (vanilla ABDA).
CLAIM(text-icon-field)

## Focus localisation contract

The focus id IS the localisation key for its name; `<id>_desc` for the
description. No `name =` field exists on focuses (unlike events). When an
AI writes a focus it must create both keys — the validator's
`missing-loc-key` rule does NOT cover focus ids (they are not event
refs), so create the loc entries in the same pass.
CLAIM(focus-loc-contract)

## End-to-end branch checklist (for one-pass authoring)

1. Plan the grid: pick x-columns that do not collide; use
   `relative_position_id` for sub-branches; reserve rows.
2. Ids: prefix with the mod namespace; grep for collisions
   (`scripts/find.py <prefix> --mod <dir>`).
3. Every focus: icon (verified sprite), cost in points (1 = 1 week),
   `search_filters` from the census above, `ai_will_do`.
4. Branch structure: `prerequisite` AND groups, `mutually_exclusive` on
   BOTH sides, `bypass` for skip paths, `will_lead_to_war_with` where
   intended.
5. Rewards: effects run in owner country scope; ideas referenced must
   exist (validator `unknown-idea-reference` catches this).
6. Localisation: `<id>` and `<id>_desc` for EVERY focus, in every
   language folder the mod ships.
7. Verify: validator zero new findings; in-game tree render + `Focus.
   AutoComplete` pass; error triage clean.
