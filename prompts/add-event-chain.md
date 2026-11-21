# Add an event chain

Give the agent your mod path and a one-line description of the chain
("two-event chain: mobilization decree → 3 days later, industry bonus").

The agent should:

1. Run first-use discovery on the mod (descriptor, namespace convention,
   loc layout) and report it.
2. Use the event kit as the base (`skills/hoi4-modding/assets/kits/event-kit/`),
   reusing the mod's existing namespace — check collisions first with
   `python tools/find.py <namespace> --mod <mod_dir>`.
3. Wire every `title`/`desc`/`name` to loc keys; create the loc entries.

Verification (mandatory before "done"):
- `python tools/validate.py <mod_dir> --data extracted/<version>` — no new
  findings.
- In-game (optional but gold): `event <namespace>.<n>` from the console,
  then `python tools/error_triage.py logs/error.log` — zero new classes.
