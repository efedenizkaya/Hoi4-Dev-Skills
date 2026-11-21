# CWTools — the complementary deep validator

Our `scripts/validate.py` is a fast, dependency-free lint that runs inside
any agent. **CWTools** ([cwtools/cwtools](https://github.com/cwtools/cwtools),
F#, .NET) is the deep, game-rule-aware validator for HOI4. They are
complements, not competitors:

| | ours (`validate.py`) | CWTools |
|---|---|---|
| Runs inside an agent loop | yes (stdlib Python, instant) | no (VS Code extension / .NET / CI) |
| Catching silent no-ops (unknown modifiers, sprites, on_actions) | yes — this is our differentiator; CWTools does not cover them | partial |
| Deep game-rule validation (cardinalities, per-field types) | no | yes |
| Maintenance (checked 2026-10-31) | active here | cwtools last commit 2025-12; **cwtools-action last commit 2023-03 — treat the Action as stale** |

## Recommended split

1. **Agent loop / local:** `scripts/validate.py` — instant feedback on
   every change; catches syntax, ids, loc, sprites, modifiers, on_actions.
2. **Game truth:** `-debug` run + `error_triage` — the final authority.
3. **CI (optional, deep):** CWTools via `cwtools/cwtools-action`. Note the
   action has not been updated since March 2023 — pin a specific version,
   expect rough edges, and treat failures as advisory unless you have
   confirmed them against the game.

## CI recipe (advisory)

```yaml
# .github/workflows/cwtools.yml — optional deep-validation job
- uses: cwtools/cwtools-action@v1.1
  with:
    game: hoi4
    modPath: ./path/to/mod
```

Requires the game's config available to the runner (usually a separate
fetch step by the maintainer) — that is why we do not enable it by default
in this repository's CI: it cannot run without game files, and committing
game data is against our license stance.
