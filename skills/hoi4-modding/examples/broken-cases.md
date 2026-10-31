# Broken cases — a mini teaching lab

Each pattern below is a real failure class with the EXACT finding the
validator produces. The regression fixtures live in the repository at
`tests/fixtures/broken/` — this page is the readable version for agents
and humans learning the failure modes.

| # | Broken pattern | What the game does | Validator finding |
|---|---|---|---|
| 1 | Event file without `add_namespace` | usually works, but popup icons default | `missing-add-namespace` (warning) |
| 2 | Event references `title`/`desc`/`name` keys that exist nowhere | raw key text shown to the player | `missing-loc-key` (error) |
| 3 | One missing brace in a focus file | THE WHOLE FILE fails to load — every focus in it vanishes | `unbalanced-braces` (error) |
| 4 | Same focus id defined twice | one copy silently wins; the other's reward never exists | `duplicate-focus-id` (error) |
| 5 | Same event id defined twice | silent duplicate; firing picks one | `duplicate-event-id` (error) |
| 6 | Decision written outside any category block | decision is invisible — no error | **not caught yet** (documented gap) |

Pattern 3 is the most destructive and the most common: a single stray
brace in an edited vanilla copy kills an entire file. Pattern 6 is the
known validator gap — when a `decision-placement` rule lands, the
fixture's expected output updates and this table changes.

## The zero-to-60 loop for any of these

```bash
python scripts/validate.py <mod_dir>
# fix what it names, then:
python scripts/error_triage.py logs/error.log --against baseline.log
```
