# Worked examples — request → routing → verification

End-to-end traces of realistic requests. Each one shows which lane the
agent takes, which references it reads, and the exact verification that
closes the task. Each ends with a "this is NOT" list to prevent scope
creep.

## Example 1: "Add a decision that gives 5% stability for 50 PP"

1. **Route**: [decisions.md](decisions.md) + the decision kit.
2. **Discover first**: `scripts/find.py <existing_namespace> --mod <dir>` —
   reuse the mod's namespace and category if one fits.
3. **Write**: decision inside the category block, `cost = 50`
   (political power), `complete_effect = { add_stability = 0.05 }`, loc
   keys wired.
4. **Verify**: `scripts/validate.py <mod_dir>` — zero new findings;
   in-game check is the user's.
- **This is NOT**: a reason to touch the mod's other decisions, or to add
  a game rule / DLC gate the user did not ask for.

## Example 2: "The game shows `myevent.1.t` instead of the event text"

1. **Route**: [symptoms.md](symptoms.md) row → loc issue.
2. **Verify**: validator `missing-loc-key` / `loc-file-encoding` rules
   pinpoint the file and line (`definite` label).
3. **Fix**: add the key to the correct language file with BOM; if the file
   was BOM-less, warn that ALL its keys were dead, not just this one.
- **This is NOT**: an excuse to rewrite the mod's localisation layout, or
  to rename keys that DO resolve.

## Example 3: "My focus tree disappeared after I added a branch"

1. **Route**: [national-focus.md](national-focus.md) common-bugs section.
2. **Check in order**: duplicate focus id (validator `duplicate-focus-id`
   covers events only — grep), tree `country` weight block still selects
   this tag, `allow_branch` trigger, file still overrides vanilla
   (same relative path).
3. **Verify**: validator clean + user confirms in-game render.
- **This is NOT**: a license to restructure the whole tree.

## Example 4: "Review my mod before release"

1. **Route**: read-only review — run `scripts/doctor.py --mod <dir>`
   (validator + duplicate ids + vanilla overrides + loc coverage in one
   report) and `scripts/error_triage.py` if the user supplies logs.
2. **Report**: findings ordered by impact, each labeled
   definite/probable/heuristic/intentional, each with file:line.
3. **Close**: list what only a game run can prove — and hand the
   `-debug` + triage procedure to the user.
- **This is NOT**: a permission to fix anything; review authorizes
  investigation only (see SKILL.md working agreement).
