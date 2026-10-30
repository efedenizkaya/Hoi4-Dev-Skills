# Create a focus branch

Give the agent the mod path, the tag, and the branch idea (3 focuses,
one mutual exclusion pair, one shared prerequisite).

The agent should:

1. Read the existing tree first (`python tools/find.py <tag> --mod <mod_dir>`
   to see what ids exist); state the x/y grid plan before writing.
2. Follow `references/national-focus.md`: `factor = 0` + per-tag modifier
   tree selection, bidirectional `mutually_exclusive`, `cost` in points
   (1 point = 1 week).
3. Wire all loc keys.

Verification (mandatory):
- `python tools/validate.py <mod_dir>` — no new findings, especially
  `missing-focus-prerequisite` / `unidirectional-mutual-exclusive` /
  `focus-position-overlap`.
- In-game: tree renders; console `Focus.AutoComplete` for a fast pass.
