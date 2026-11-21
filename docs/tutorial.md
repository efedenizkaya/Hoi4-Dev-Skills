# Tutorial: from zero to a verified event

A complete first pass through the workflow: install, extract your game's
data, create an event in a fresh mod, and verify it the way the skill does.
Time: ~15 minutes once HOI4 is installed.

## 0. Prerequisites

- Hearts of Iron IV (Steam) installed, run at least once
- Python 3.10+ and git
- An AI agent (Claude Code, Codex, Cursor, …) — optional but the point

## 1. Get the project and the skill

```bash
git clone https://github.com/efedenizkaya/Hoi4-Dev-Skills.git
cd Hoi4-Dev-Skills
./install.sh          # or: powershell -ExecutionPolicy Bypass -File install.ps1
pip install pytest && python -m pytest   # should end: N passed
```

## 2. Extract your game's data

```bash
python tools/extract.py
```

Expected output:

```
game version : 1.19.4.1
effects      : 553
triggers     : 596
modifiers    : 1132 across 19 scopes
written to   : extracted\1.19.4.1
```

If the game was not found, set `HOI4_GAME_DIR` to the install folder
(`C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV`) and
retry. This data is exact for **your** patch and stays on your machine.

## 3. Create a fresh mod (do NOT touch existing mods)

In `Documents/Paradox Interactive/Hearts of Iron IV/mod/` create two files:

`my_first_mod.mod`:

```txt
version="0.1.0"
tags={
	"Events"
}
name="My First Mod"
supported_version="1.19.*"
path="mod/my_first_mod"
```

`my_first_mod/descriptor.mod`: same fields, without the `path` line.

## 4. Write the event from the kit

Copy the event kit into the mod:

```bash
cd "Documents/Paradox Interactive/Hearts of Iron IV/mod"
mkdir my_first_mod
cp -R <repo>/skills/hoi4-modding/assets/kits/event-kit/* my_first_mod/
```

Then rename `mymod` → `firstmod` everywhere (file names included). Open
`events/firstmod_events.txt` — one event with two options, one of which
fires a follow-up event after 3 days. Notice the localisation file carries
the BOM already.

Point your agent at the task instead, if you like: *"use the hoi4-modding
skill to add a third option to firstmod.1 that requires 100 political
power and gives 5% stability"*.

## 5. Static verification (lane 1)

```bash
python tools/validate.py "mod/my_first_mod"
```

Expected: `0 error(s), 0 warning(s)` (the kit is validator-clean by
design). Try breaking something to see the rules fire: duplicate the event
id in a second file, or delete a loc key — the validator names the rule,
file, and line.

## 6. Game run + error.log triage (lanes 2–3)

1. Launch the game once now, quit to desktop → a baseline `error.log`
   exists.
2. Copy it: `logs/error.log` → `logs/baseline.log`.
3. Enable the mod in the launcher, launch again, quit to desktop.
4. Diff:

```bash
python tools/error_triage.py "logs/error.log" --against "logs/baseline.log"
```

All-zero deltas = your mod introduced nothing. In game, open the console
(debug mode required for some commands — see
[the debugging reference](../skills/hoi4-modding/references/debugging-and-logs.md))
and fire the event: `event firstmod.1`.

## 7. Where to go next

- [setup-game-data.md](setup-game-data.md) — what the extractor reads
- The [skill's references](../skills/hoi4-modding/SKILL.md) — focus trees,
  decisions, characters, MIOs…
- [CONTRIBUTING.md](CONTRIBUTING.md) — how claims stay grounded
