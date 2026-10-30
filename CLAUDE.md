# CLAUDE.md

Read `skills/hoi4-modding/SKILL.md` before any Hearts of Iron IV modding
task in this repository. It defines the verification loop, the working
agreement, and the routing table.

Quick commands (repo root):

```bash
python tools/validate.py <mod_dir> --data extracted/<version>   # static lint
python tools/find.py <pattern> --mod <mod_dir>                  # where is X defined
python tools/error_triage.py logs/error.log --against baseline.log
python tools/extract.py                                         # refresh game data
```

Game behavioral claims must be traceable to `docs/claims-register.md`.
