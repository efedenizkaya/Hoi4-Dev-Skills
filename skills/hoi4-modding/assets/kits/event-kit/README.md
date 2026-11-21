# Event kit

A minimal, validator-clean event pair (one country event, one follow-up
option-fired event). Replace `mymod` with your mod namespace everywhere
(including file names), then:

1. Copy `events/` and `localisation/` into your mod folder.
2. `python tools/validate.py <mod_dir>` — expect no new findings.
3. In game (debug console): `event mymod.1`

Files:

- `events/mymod_events.txt` — the script
- `localisation/english/mymod_events_l_english.yml` — UTF-8 with BOM loc
