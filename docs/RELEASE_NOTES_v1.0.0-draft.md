# Release v1.0.0 — draft notes (owner edits before tagging)

## hoi4-dev-skills v1.0.0

The first stable release of a verified, game-derived Agent Skill and
tooling for AI-assisted Hearts of Iron IV modding.

### Highlights

- **Agent Skill** (`skills/hoi4-modding/`): Agent-Skills-spec compliant —
  router + 27 references + 6 validator-clean asset kits + 162 sourced
  claims. Verified against HOI4 **1.19.4.1** (Operation Postern).
- **13 tools**: extract (game docs → version-stamped JSON), validate
  (static lint + silent-failure rules), error_triage, doctor (health
  score), find (identifier index), chain_map, override_audit,
  loc_report, loc_sync, version_diff, stale_check, new_mod — all
  stdlib-Python, all tested.
- **Read-only MCP server** exposing 8 tools over the same
  implementations.
- **Verified on a real hand-made mod**: the dogfood census (833 duplicate
  loc keys, 34 dangling event targets, 18 phantom sprites, 11 vanilla
  overrides) is published in docs/dogfood-lessons.md.
- **CI**: 129 tests + eval gates + skills-ref validation + installer
  smokes + packaged `.skill` artifact on every push.

### Requirements

- HOI4 (Steam) + Python 3.10+ for the tools. The skill itself installs
  like any Agent Skill (see docs/INSTALLATION.md).

### Known limitations

- CI runs on the maintainer's self-hosted Windows runner (single OS).
- Runtime verification (launching the game) remains a manual step.
- Claims labeled `unverified` in docs/claims-register.md are plausible
  community knowledge awaiting game-install verification.

## Owner release checklist (do these, in order)

1. **Billing**: Settings → Billing and plans → resolve the failed
   payment / raise the spending limit IF you want GitHub-hosted runners
   back. Not required for release — self-hosted CI is green.
2. **Version sync**: metadata.json, pyproject.toml and the top CHANGELOG
   entry must all say the release version (test_versions_consistent
   enforces the first two).
3. **Tag**: `git tag -a v1.0.0 -m "v1.0.0" && git push origin v1.0.0`.
4. **GitHub Release**: create from the tag, paste the notes above (edit
   freely), attach the `hoi4-modding-skill` artifact from the latest CI
   run (or re-zip `skills/hoi4-modding/`).
5. **Visibility decision**: repo is private. Public → free Actions
   minutes + Dependabot visibility; the codebase contains no personal
   paths or game data (audited), so publishing is safe from the content
   side. Your call, no deadline.
6. **After publishing**: enable secret scanning + Dependabot alerts in
   Settings → Advanced Security; consider Discussions categories for
   the game-update flow.
7. **Announce** (optional): the Agensi listing, r/hoi4modding, the
   Paradox modding forum — using the "First things to try" prompts from
   the README.
