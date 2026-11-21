# Characters kit

One character, three roles (country leader, political advisor, corps
commander) — the advisor carries its own `idea_token` for the ledger.
Replace `mymod` and the token everywhere.

1. Copy `common/` and `localisation/` into your mod.
2. Add `recruit_character = mymod_leader` to the owning country's history
   file — without it the character exists but never appears.
3. `python scripts/validate.py <mod_dir>` — expect no findings.
