# Events

Event types in the current game: `country_event`, `news_event`,
`state_event`, `unit_leader_event` (all exist as effects in 1.19.4.1 —
verified against `effects.json`). Events live in `<mod>/events/*.txt`.

CLAIM(event-types)

## Anatomy

```txt
country_event = {
	id = mymod.1              # namespace.number — must be unique
	title = mymod.1.t         # localisation keys derived from the id
	desc = mymod.1.d
	picture = GFX_report_event_generic_sign_treaty1

	is_triggered_only = yes   # block PROPERTY, not a trigger: event fires
	                          # only via the `country_event` effect / on_actions
	fire_only_once = yes      # block PROPERTY: never fires twice
	hidden = yes              # block PROPERTY: player sees nothing

	trigger = {               # actual TRIGGER block: conditions to fire
		has_dlc = "Waking the Tiger"
	}

	immediate = {             # effects run when the event fires, before display
		set_country_flag = mymod_1_fired
	}

	option = {
		name = mymod.1.a
		# effects here run when the player picks this option
	}
	option = {
		name = mymod.1.b
		trigger = { has_political_power > 100 }   # option-visibility trigger
		ai_chance = { factor = 2 }
	}
}
```

CLAIM(event-properties-not-triggers)

- `is_triggered_only`, `fire_only_once`, `hidden`, `major`, `fire_for_sender`
  are **fields of the event block**, not triggers — writing them inside
  `trigger = { }` does nothing.
- Without `is_triggered_only = yes`, the event's `trigger` block is evaluated
  continuously (on_actions/pulse) — a common cause of "event fires randomly".
  CLAIM(pulse-trigger-continuous) `[unverified]`

## Namespace and IDs

An event file may declare its namespaces up front — vanilla does this in
every file (e.g. `AAT_Generic_Events.txt`):

```txt
add_namespace = {
	name = mymod
	icon = GFX_report_event_generic_sign_treaty1
}
```

This sets the namespace's icon/background for the event popup; the events
below then use `id = mymod.<n>` as usual. CLAIM(add-namespace)

- `id = <namespace>.<number>`; the namespace is a plain word without dots
  (declare it with `add_namespace` for proper popup icons — see above).
  Related events share a namespace (`mymod.1`, `mymod.2`).
- IDs must be unique across the whole game (mod + vanilla + other mods).
  CLAIM(event-id-uniqueness) `[unverified]`
  `tools/validate.py` reports duplicates (`duplicate-event-id`) and flags
  single re-definitions of a vanilla id as `vanilla-event-override` — that is
  the standard way to replace a vanilla event; keep it deliberate.
- News events shown to all countries: `major = yes` on a `news_event`.
  CLAIM(news-major-all) `[unverified]`

## Localisation contract

Every `title`/`desc`/`name` needs a key `<id>.t`, `<id>.d`, `<id>.a`
(option letters continue `.b`, `.c`, …). Option descriptions can use
`<id>.a.d` (custom_tooltip style keys are also common). The validator's
`missing-loc-key` rule checks event loc refs against the mod's
`localisation/**/*.yml` and the base game's `english` folder.

CLAIM(loc-key-convention)

## Firing an event from script

```txt
country_event = { id = mymod.1 days = 2 }        # in ROOT's country scope
country_event = { id = mymod.1 hours = 6 random = 12 }
news_event = { id = mymod_news.3 }
```

`days`/`hours` delay the event; `random` adds a random extra delay. The event
fires for the current scope (country) unless `root =`/`received` overrides
are used — check the effect's entry in `effects.json` for exact fields
per version rather than relying on memory.

CLAIM(fire-delay-fields)

## MTTH vs trigger events

Pulse events (no `is_triggered_only`) may instead use `mean_time_to_happen`
(`mtth`):

```txt
country_event = {
	id = mymod.10
	mean_time_to_happen = {
		days = 720
		modifier = { factor = 0.5 has_idea = war_economy }
	}
	trigger = { ... }
}
```

## Worked example (event-kit)

A complete, validator-clean event lives in
[../assets/kits/event-kit/](../assets/kits/event-kit/MANIFEST): event file,
localisation file, and the exact commands to verify.

## Verification steps

1. `python tools/validate.py <mod_dir>` — zero new errors.
2. Fire it from console (`event mymod.1`) with the user, or from a focus
   completion; then `python tools/error_triage.py logs/error.log` — no new
   `invalid-scope` / missing-loc classes.
3. For scheduled events confirm the `immediate` effects ran (flag/variable).

## Complete event field reference (vanilla census, 1.19.4.1)

Frequency = occurrences across all vanilla `events/*.txt`:

| Field | Freq | Notes |
|---|---|---|
| `option` | 11565 | at least one required |
| `id` | 11212 | `namespace.number` |
| `desc`, `title` | ~7000 | loc keys, or multi-desc block (below) |
| `picture` | 6783 | `GFX_report_event_*` sprite |
| `is_triggered_only` | 6581 | block property, not a trigger |
| `fire_only_once` | 1398 | block property |
| `hours` / `days` | 1164 / 848 | on the FIRING effect (`country_event = { id = x hours = 6 }`) |
| `immediate` | 961 | effects run at fire time, before display |
| `trigger` | 714 | pulse conditions (omit with `is_triggered_only`) |
| `major` | 627 | news_event shown to everyone |
| `mean_time_to_happen` | 377 | pulse alternative; `days = N` + `modifier = { factor }` |
| `random_days` / `random_hours` | 311 / 238 | random extra delay on the firing effect |
| `hidden` | 239 | player sees nothing; options still required |
| `fire_for_sender` | 36 | news/country events also shown to the sender |
| `timeout_days` | 6 | for event menus with expiry |
| `months` / `random` | rare | delay variants |
| `show_major` / `minor_flavor` / `after` | rare | |

### Conditional description (vanilla WTT_Germany.txt)

```txt
desc = {
	text = wtt_germany.28.d
	trigger = { NOT = { ... } }
}
desc = {
	text = wtt_germany.28.d.2
	trigger = { ... }
}
```

The FIRST block whose trigger passes wins. CLAIM(multi-desc)

### Complete option field set (census)

`name` (always), `ai_chance` (6270), `trigger` (3279), `hidden_effect`
(2047 — effects run but show no tooltip), `custom_effect_tooltip`
(1558), `effect_tooltip` (1205), plus any effects. CLAIM(option-census)
