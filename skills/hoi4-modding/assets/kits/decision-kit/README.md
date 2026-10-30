# Decision kit

A decision category with two decisions embedded inside it (one repeatable,
one one-shot) — vanilla's standard pattern (see `common/decisions/AFG.txt`).
Replace `mymod` everywhere. `cost` is political power by default.

1. Copy `common/` and `localisation/` into your mod folder.
2. `python tools/validate.py <mod_dir>` — expect no new findings.
3. In game: the decisions appear under the Politics decisions tab when
   `visible` holds.
