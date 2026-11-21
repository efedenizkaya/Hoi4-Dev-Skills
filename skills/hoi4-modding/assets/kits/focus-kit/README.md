# Focus kit

A minimal focus tree: two mutually exclusive branches sharing one
prerequisite chain — validator-clean (focus rules active). Replace `mymod`
everywhere; set the owning tag in the tree's `country` modifier.

1. Copy `common/` and `localisation/` into your mod.
2. `python scripts/validate.py <mod_dir>` — expect no findings.
3. In-game: tree appears for the tag in the `country` block; console
   `Focus.AutoComplete` (debug) for a fast pass.
