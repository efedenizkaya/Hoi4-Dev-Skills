# Broken cases — broken/fixed pairs

Six real failure classes, each with a BROKEN and a FIXED snippet and the
exact validator finding. The machine-checkable regression fixtures for
these live in the repository at `tests/fixtures/broken/`.

## 1. Event file without `add_namespace`

**Broken** — popup icons fall back to defaults; the declaration is the
convention in all 128 vanilla event files:

```txt
country_event = {
	id = mymod.1
	...
}
```

**Fixed:**

```txt
add_namespace = mymod

country_event = {
	id = mymod.1
	...
}
```

Finding: `missing-add-namespace` (warning).

## 2. Localisation keys that exist nowhere

**Broken** — the player sees raw `mymod.1.t` text:

```txt
country_event = {
	id = mymod.1
	title = mymod.1.t
	desc = mymod.1.d
```

**Fixed** — keys created in a BOM'd file (create BOTH, always):

```yml
l_english:
 mymod.1.t:0 "An Event"
 mymod.1.d:0 "Something happened."
```

Finding: `missing-loc-key` (error), one per missing key.

## 3. One missing brace kills an entire file

**Broken** — `completion_reward` never closes, so the SECOND focus does
not exist and the whole tree may fail to parse (this exact shape is the
most destructive and most common failure in real mods):

```txt
focus = {
	id = mymod_rearm
	icon = GFX_focus_generic_industry_3
	completion_reward = {
		add_political_power = 50

focus = {
	id = mymod_industry
```

**Fixed** — brace closed before the next block:

```txt
	completion_reward = {
		add_political_power = 50
	}
}
```

Finding: `unbalanced-braces` (error).

## 4. Duplicate focus id

**Broken** — one copy silently wins; the other focus and its reward do
not exist:

```txt
focus = {
	id = mymod_rearm
	...                     # grid (1, 0)
}
focus = {
	id = mymod_rearm        # same id!
	...                     # grid (2, 0)
}
```

**Fixed** — unique ids (`mymod_rearm`, `mymod_industry`).

Finding: `duplicate-focus-id` (error).

## 5. Duplicate event id across files

**Broken** — two definitions, the game keeps one:

```txt
# events/a.txt
country_event = { id = mymod.1 ... }
# events/b.txt
country_event = { id = mymod.1 ... }
```

**Fixed** — renumber, or deliberately override a vanilla event ONCE
(which the validator downgrades to `vanilla-event-override`).

Finding: `duplicate-event-id` (error).

## 6. Decision outside any category block

**Broken** — the decision loads but is INVISIBLE: no error, no button:

```txt
# common/decisions/stray.txt
mymod_decision = {
	icon = generic_industry
	visible = { always = yes }
}
```

**Fixed** — decisions must live inside their category block (or the
category must be referenced per the version's grammar):

```txt
mymod_category = {
	icon = generic_political_actions

	mymod_decision = {
		icon = generic_industry
		visible = { always = yes }
	}
}
```

**Validator status: NOT CAUGHT YET** — this is the documented gap
(`decision-placement` rule pending). The regression fixture
`tests/fixtures/broken/decision-outside-category/` fails loudly the day
the rule lands.

## The loop

```bash
python scripts/validate.py <mod_dir>
# fix, then prove it:
python scripts/error_triage.py logs/error.log --against baseline.log
```
