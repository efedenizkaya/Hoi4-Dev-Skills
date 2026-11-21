# Lessons from a real hand-made mod

Everything on this page was found by running this repo's tools against a
real, actively-played, hand-made country mod (~19k lines, 9 focus files,
4 event files, 5 localisation languages, game version 1.19.4.1). No
competitor project publishes real-mod failure data — this is ours,
sanitized (no paths, no mod name).

## The failure census

| Finding class | Count | What the tools said |
|---|---|---|
| Duplicate loc keys in one file | 833 | last definition silently wins |
| Missing localisation keys | dozens | players see raw `ns.1.t` text |
| Fired events that are defined nowhere | 34 | the chain just stops, silently |
| Idea tokens added that exist nowhere | 13 | silent no-op effects |
| Dangling focus prerequisites | several | branches permanently locked |
| Sprites referenced that exist nowhere | 18 | placeholder icons, NO error |
| Unbalanced braces | 1 | one file's entire content dead |
| Exact vanilla file overrides | 11 | each one is a future patch-break |

Two patterns dominate everything: **silent no-ops** (undefined ideas,
sprites, events — the game does nothing and logs nothing) and
**whole-file fragility** (one brace or one stale vanilla copy).

## What this taught the tooling

Each tool feature below exists because a real finding demanded it:

- `loc-language-mismatch` needed subfolder semantics (files live in
  `english/events/`, not directly in the language folder) — the first
  version produced 800+ false positives.
- The duplicate-focus-id rule exists because the collector's dict
  silently kept one copy.
- `unknown-sprite` was added because sprite typos are invisible in
  error.log — it immediately found 18 real ones, including inside our
  own example kits.
- Quote masking keeps BOTH quote characters so an unclosed string is
  countable — the first version flagged every paired string.
- The statement-name check only reads depth-1 of effect blocks: effect
  argument schemas (`add_building_construction = { building = ... }`)
  are their own grammar and naive scanning produced 11.5k false alarms.

## The meta-lesson

Hand-made mods accumulate silent no-ops because the game forgives
everything except parse errors. A mod can ship for years with dead
focuses, dead ideas and dead events — players never complain because
there is nothing to complain ABOUT. Tooling is the only way to see it.

## Rebuilding this census on your own mod

```bash
python tools/doctor.py --mod <mod_dir> --out report.md
```

One command, full report, health score included.
