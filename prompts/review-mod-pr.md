# Review a mod (or a mod PR)

Give the agent the mod path and — for a PR — the changed file list.

The agent should:

1. Stay read-only (review authorizes investigation, not changes).
2. Run `python scripts/validate.py <mod_dir> [--data extracted/<version>]`
   and classify every finding: definite / probable / heuristic /
   intentional (a vanilla-event redefinition is `intentional`, not a bug).
3. Trace changed identifiers with `python scripts/find.py <id> --mod
   <mod_dir> --game-dir <game>` — who references them, who breaks if they
   change.
4. Lead with concrete findings ordered by impact, each with file:line
   evidence and a label. If no defect is established, say so and list the
   remaining test gaps (what only a game run can prove).
