# Evals

Two layers:

## 1. Trigger evals (`trigger-evals.json`)

Queries with `should_trigger` — regression data for the skill's
description matching. Reviewed by hand when SKILL.md's description
changes.

## 2. Task evals (`task-evals.json` + `scripts/run_evals.py`)

Each entry = a task prompt, a mod directory, and validator expectations.

- **Gold mode** (CI): `python tools/run_evals.py --evals evals/task-evals.json --self-test`
  — proves the shipped kits satisfy their own gates.
- **Agent mode**: run the task with your agent into its own mod dir, point
  the entry's `mod_dir` at it, run without `--self-test`. Exit 0 = all
  gates pass.
- Game-truth verification (error.log diff) stays a documented manual step —
  see docs/setup-game-data.md.
