# Debug the error log

Give the agent the mod path (and the log path if non-default).

The agent should:

1. Run `python scripts/error_triage.py <log>` for the classified picture.
2. For each class, map to the fix playbook (see
   `skills/hoi4-modding/references/debugging-and-logs.md` and
   `references/symptoms.md`), with finding labels
   (definite/probable/heuristic).
3. Propose fixes as a diff plan — do not modify files unless asked.

Verification (mandatory after fixes):
1. Capture a fresh baseline `error.log`.
2. Apply fixes, launch with `-debug`.
3. `python scripts/error_triage.py logs/error.log --against baseline.log`
   — exit 0, no positive deltas.
