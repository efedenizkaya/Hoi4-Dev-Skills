# Agent instructions for this repository

This repo contains an [Agent Skills](https://agentskills.io)-compliant
skill for Hearts of Iron IV modding plus the verification tools it uses.

- Skill entry point: `skills/hoi4-modding/SKILL.md` — read it before any
  HOI4 modding task; it routes to references and defines the verification
  loop.
- Tools (run from this repo root): `python tools/validate.py <mod_dir>`,
  `python tools/extract.py`, `python tools/error_triage.py …`,
  `python tools/find.py …`, `python tools/new_mod.py …`. The same
  implementations ship inside the skill under
  `skills/hoi4-modding/scripts/` for installed use.
- Rules of engagement: the skill's **Working agreement** section
  (first-use discovery, review ≠ modify, finding labels,
  `definite/probable/heuristic/intentional`, response template).
- Every behavioral claim about the game is sourced in
  `docs/claims-register.md`; never state game behavior as fact without a
  source or an explicit `unverified` label.

Adapters for specific agent platforms live in `adapters/`.
