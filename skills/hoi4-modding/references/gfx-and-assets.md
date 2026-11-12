# GFX and assets

Two pieces connect: a **sprite declaration** in `interface/*.gfx` naming a
**texture file** under `gfx/`. Script references the sprite name.

## Sprite declaration

`interface/mymod_gfx.gfx`:

```txt
spriteTypes = {
	SpriteType = {
		name = "GFX_focus_mymod_industry"
		texturefile = "gfx/interface/goals/focus_mymod_industry.dds"
	}
	corneredTileSpriteType = {       # for 9-slice UI panels
		name = "GFX_tiled_panel_mymod"
		texturefile = "gfx/interface/panel_mymod.dds"
	}
}
```

- Sprite names are quoted; the file path is relative to the mod root.
- A focus `icon = GFX_focus_mymod_industry` needs exactly that sprite — a
  missing one renders the "unknown" placeholder **without an error**;
  a missing texture file is a real `error.log` line.
  CLAIM(missing-sprite-silent)

## Image formats

| Use | Format | Notes |
|---|---|---|
| Event pictures, focus icons, portraits | **DDS** (DXT1/5) | vanilla standard; power-of-two sizes |
| Older assets / some flags | TGA | still accepted |
| Flags | `gfx/flags/<tag>.tga` + `gfx/flags/medium/`, `small/` | fixed sizes per folder |
| Leader portraits | DDS in `gfx/leaders/<TAG>/Portrait_*.dds`; sprites declared in `interface/_leader_portraits.gfx` | characters reference `GFX_portrait_*` names directly |

CLAIM(image-formats)

Flags for a new tag need all three sizes (`small/` and `medium/` variants);
missing sizes show as blank in some UIs. CLAIM(flag-sizes)

## Event pictures

Event `picture = GFX_report_event_...` — sprite defined in
`interface/eventpictures.gfx` (vanilla) or your own file; texture under
`gfx/event_pictures/`. Reusing vanilla GFX names is fine and saves work —
list them via `grep GFX_report_event <game>/interface/eventpictures.gfx`.

## Load order for .gfx

`interface/` files are additive: your `mymod_gfx.gfx` adds sprites; a file
with the same name as a vanilla one replaces it wholesale (see
[mod-structure.md](mod-structure.md)). Font/`fonts.gfx` overrides are the
usual way to change fonts. CLAIM(gfx-additive) `[unverified]`

## Verification steps

1. `python tools/validate.py <mod_dir>` (script-side only).
2. Launch and check `error.log` for missing texture/entity lines; remember
   sprite-name typos do NOT appear there — check the UI visually.
3. DDS conversion: any image editor with the DDS plugin; use DXT1 for
   opaque, DXT5 when alpha is needed.

## Complete SpriteType field reference (vanilla census, 1.19.4.1)

8951 `name` / 8816 `texturefile` pairs across `interface/*.gfx`, plus:

| Field | Freq | Notes |
|---|---|---|
| `noOfFrames` | in goals.gfx | icon STRIPS: one texture, N frames; loc picks with `£icon|frameNo` |
| `effectFile` | 3416 | `.fxh` shader attachment (PDX FX system) |
| `animation` family | 6347 | `animation`, `animationmaskfile`, `animationtexturefile`, `animationrotation`, `animationlooping`, `animationtime`, `animationdelay`, `animationblendmode`, `animationtype`, `animationrotationoffset`, `animationtexturescale` — animated sprites (radar pings, shimmering focuses) |

Other sprite kinds in .gfx: `corneredTileSpriteType` (9-slice panels),
`progressBarType` (e.g. powerbalanceview.gfx), `bitmapfonts`/font blocks
separately. CLAIM(sprite-census)

### Icon strips (the £ connection)

A `noOfFrames = 5` sprite feeds `£token|3` in localisation (frame 3 of 5).
When a modded icon shows the WHOLE strip, the frame index or noOfFrames is
wrong — this pairs with `loc-icon-syntax`. CLAIM(sprite-strips)

## Entities and unit models (3D)

Unit/ship models are **entities**: `entity = { name = "..."; pdxmesh = "..."; default_state / state = { name animation ... } }` blocks in `gfx/entities/*.asset` files (one file per domain: units_infantry.asset, units_artillery.asset, _units_battleships_DLC.asset, MTG_buildings.asset, ...). The `pdxmesh` references a `.mesh` + animations under `gfx/models/`.

Resolution order when something asks for `GER_infantry_entity` (from the raids documentation, same lookup everywhere): country-specific override → culture-specific override → base entity → `default_entity`.

Claiming a new unit model means: `.mesh` + animations under `gfx/models/`, an `entity` block in a `.asset` file, and (for raids) the `unit_model` block in the raid type. Wrong entity names fall down the resolution chain silently — only a completely missing default logs. CLAIM(entities-asset-files)

Also in `.gfx` files beyond sprites: `spriteType`/`corneredTileSpriteType`/`progressBarType`, and `bitmapfonts`/font blocks. Screen effects are `.fxh`/`.shader` files under `gfx/FX/` (advanced; see the game's own shader examples).
