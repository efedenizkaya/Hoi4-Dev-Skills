# Map modding — high blast radius, read this first

Everything under `map/` is **binary/CSV territory**: errors here can
crash the game at startup with unhelpful logs, and most of it cannot be
validated by any script — the game itself is the only oracle. This page
orients; it does not replace the dedicated map-modding community guides.

CLAIM(map-warning-first)

## The load-bearing files

| File | What it is | Breakage symptom |
|---|---|---|
| `definition.csv` | province registry: id, R,G,B, type (land/sea/lake), coastal, terrain | startup crash, "Loaded N provinces" count wrong in game.log |
| `provinces.bmp` | province color map — every pixel's RGB must match a definition.csv row | startup crash |
| `heightmap.bmp` | elevation | visual weirdness, pathing |
| `terrain.bmp` | terrain per pixel | wrong terrain everywhere |
| `cities.bmp`, `rivers.bmp` etc. | overlays | visual |
| `positions.txt` | per-province anchor points (units, cities, text) | units floating/misplaced |
| `adjacencies.csv` + `adjacency_rules.txt` | non-standard connections | can't cross where you should |
| `strategicregions_*.csv` | air/supply regions | supply warnings in error.log |
| `buildings.txt` (in map/) | where map buildings render | |
| `railways.txt` (NSB+) | supply rail network | supply collapse |
| `supply_nodes.txt` | hubs | supply collapse |
| `default.map`, `continent.txt`, `colors.txt` | world plumbing | startup issues |

CLAIM(map-load-bearing)

## Risk tiers

- **Low risk**: re-assigning existing provinces between states (pure
  `history/states/` edit — see [map-states-and-history.md](map-states-and-history.md)).
- **Medium**: editing `strategicregions`, `railways`, supply nodes —
  CSVs, diffable, errors usually logged.
- **High**: adding/moving provinces (definition.csv + provinces.bmp +
  heightmap + positions + buildings.txt must stay consistent), which also
  invalidates every save and most map screenshots. Use a dedicated tool
  (community map editors); do this by hand only in emergencies.
- **Extreme**: `default.map`, world sizes, lake/sea re-zoning.

CLAIM(map-risk-tiers)

## Verification (limited)

1. `game.log`: `Loaded N provinces` — count matches your definition.csv
   row count for land provinces.
2. `error.log`: supply/strategic-region classes.
3. Visual pass: political + supply + terrain map modes.

If the game crashes on startup after a map edit, revert first, bisect
second — error.log rarely names the map culprit.
