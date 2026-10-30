# Mod structure, .mod files and compatibility

## The `.mod` descriptor pair

A playable mod needs a folder plus a `.mod` file next to it:

```
mod/
├── mymod/            # the mod folder
└── mymod.mod         # the descriptor
```

`mymod.mod`:

```txt
version="1.0.0"
tags={
	"Historical"
	"Focus Tree"
}
name="My Mod"
supported_version="1.19.*"
path="mod/mymod"
```

- `path` is relative to the user directory (`Documents/Paradox Interactive/
  Hearts of Iron IV/`) — CLAIM(mod-path-relative)
- Workshop-hosted mods carry a `remote_file_id="..."` instead of a local
  folder; a local `path` pointing at the same content overrides it.
- A second `descriptor.mod` inside the mod folder is required for Workshop
  uploads (same fields, no `path`). CLAIM(descriptor-inside)
- `supported_version` mismatch triggers the load-warning screen; wildcard
  `1.19.*` survives minor patches.

## Folder map (what the game reads from a mod)

| Folder | Contents |
|---|---|
| `common/` | definitions: national_focus, ideas, decisions, characters, ai_strategy, modifiers, scripted_effects/triggers, MIO … |
| `events/` | event scripts |
| `history/countries/` | starting state per tag: `GER - Germany.txt` style names, `add_ideas`, `set_technology`, oob ids |
| `history/states/` | state definitions |
| `localisation/<language>/` | `l_english:` blocks, UTF-8 **with BOM**, spaces for indentation |
| `interface/` | `.gfx` sprite declarations, `.gui` layouts |
| `gfx/` | actual images referenced by sprites |
| `map/` | (rarely touched; heavy overrides) |
| `sound/`, `music/` | audio |
| `thumbnail.png` | mod browser image |

CLAIM(folder-map)

## Override and load order rules

1. The game loads vanilla first, then each mod (in playset order). A mod
   **file with the same relative path replaces** the vanilla file entirely —
   partial changes require copying the whole vanilla file, not just your
   addition. CLAIM(full-file-replace)
2. `common/` **subfolders are additive by filename**: `common/ideas/
   mymod_ideas.txt` adds new entries without touching vanilla files — until
   a filename collides, then rule 1 applies. CLAIM(additive-subfolders)
3. `replace_path = "common/land_doctrines"` style fields in the descriptor
   make the game skip vanilla content in that path entirely (use sparingly;
   breaks compat with mods relying on vanilla content). CLAIM(replace-path)
4. Within one playset, later mods in the list win file collisions — this is
   the usual source of "works alone, breaks in playset" reports.

## Compatibility practice

- Prefer additive filenames over replacing vanilla files.
- Never edit another mod's files in your own repo; override by loading order
  or by re-defining identifiers deliberately (validator reports those as
  `vanilla-event-override` for events).
- State your `supported_version` honestly; test against the current patch
  with the verification loop in SKILL.md.

## Verification steps

1. Descriptor parses: the mod appears in the launcher, no warning triangle.
2. `python tools/validate.py <mod_dir>` — full pass.
3. Game boots to lobby with the mod enabled and `logs/error.log` contains no
   mod-path errors: `python tools/error_triage.py logs/error.log`.
