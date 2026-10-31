# CLAUDE.md — HOI4 mod repository

Use the hoi4-dev-skills skill (`skills/hoi4-modding/SKILL.md` or the
installed copy) for every Hearts of Iron IV task here.

Commands (adjust the tools path to your checkout):

```bash
python <tools-path>/validate.py .          # static lint — run after every change
python <tools-path>/find.py <pattern> --mod .
python <tools-path>/error_triage.py logs/error.log --against baseline.log
```

Working agreement, routing table and finding labels: see the skill.
