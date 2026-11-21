# Version migration workflow (new HOI4 patch)

A patch lands → reference data goes stale → this is the ordered recovery
run. Every step uses a tool that ships with this skill.

## 1. Capture the new baseline

```bash
python scripts/extract.py --summary-out docs/data-summaries/<new_version>.json
```

Game version comes from `launcher-settings.json`; the summary is
counts-only and safe to attach to a `game update` issue.

## 2. Diff against the previous version

```bash
python scripts/version_diff.py extracted/<old_version> extracted/<new_version>
```

Read the added/removed effects, triggers and modifiers as three questions:

- **Removed** — does any claim row or reference example use them? (grep
  the skill references; update or tag `unverified`.)
- **Added** — worth new examples? Add only what is verifiable.
- **Modifiers changed** — re-run the validator on a real mod: the
  `unknown-modifier-name` rule now speaks with the NEW database; a rule
  that "was fine" may start warning because the modifier was renamed.

## 3. Inventory full-file overrides

```bash
python scripts/override_audit.py --mod <mod_dir> --game-dir <game>
```

Every `exact-replace` row is a file whose vanilla counterpart changed in
the patch — the stale mod copy now hides the new content. Refresh or
convert to additive (see [mod-structure.md](mod-structure.md)).

## 4. Re-verify the claims register

- Rows whose Source cites the old version's docs/files: re-check against
  the new install, update the `Checked` date.
- Rows marked `**unverified**`: a patch is the perfect moment to promote
  them — verify one, remove the marker, note the source.
- Update the version stamp in `SKILL.md` (`game-version-verified`) ONLY
  after steps 1–3 ran clean on your install.

## 5. Verify real mods

```bash
python scripts/validate.py <mod_dir> --data extracted/<new_version>
python scripts/error_triage.py logs/error.log --against baseline.log
```

Static and runtime evidence stay separate: static passes never prove
runtime behavior — say so explicitly.

## What NOT to do

- Do not trust patch notes as documentation; a shipped schema can lag the
  patch — verify against the regenerated `documentation/*.md` files.
- Do not batch-update claim rows you have not actually re-checked; leave
  them stale and marked instead.
