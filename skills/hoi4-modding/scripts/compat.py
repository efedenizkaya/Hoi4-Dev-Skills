"""Compatibility Lab: conflict detection across multiple mods.

Indexes every mod (identifier index, vanilla-shadow inventory,
localisation keys) and reports cross-mod collisions:
- same identifier defined in two or more mods (events, focuses, ideas,
  decisions, characters, scripted effects/triggers)
- several mods shadowing the same vanilla file (exact-replace fights;
  playset order decides the winner)
- same localisation key defined by several mods

Analysis only — mods are never modified. Vanilla-aware: definitions
present in the base game are not reported as cross-mod collisions.

Usage:
    python tools/compat.py --mod <dir> --mod <dir2> [...] [--json]

Exit codes: 0 = no conflicts, 1 = conflicts found, 2 = usage error.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import json
import sys
from pathlib import Path

try:
    from .extract import find_game_dir
    from .find import index_mod
    from .loc_report import _LOC_KEY_RE as _KEY_RE
    from .override_audit import _vanilla_files
except ImportError:
    from extract import find_game_dir
    from find import index_mod
    from loc_report import _LOC_KEY_RE as _KEY_RE
    from override_audit import _vanilla_files


def _loc_keys(mod_dir: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    loc = mod_dir / "localisation"
    if not loc.is_dir():
        return out
    for path in sorted(loc.glob("**/*.yml")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        rel = str(path.relative_to(mod_dir))
        for m in _KEY_RE.finditer(text):
            out.setdefault(m.group(1), []).append(f"{rel}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-mod conflict detection (Compatibility Lab)")
    parser.add_argument("--mod", type=Path, action="append", required=True,
                        help="mod directory (repeat for each mod)")
    parser.add_argument("--game-dir", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if len(args.mod) < 2:
        print("error: pass --mod at least twice (compat needs 2+ mods)",
              file=sys.stderr)
        return 2
    for d in args.mod:
        if not d.is_dir():
            print(f"error: {d} is not a mod directory", file=sys.stderr)
            return 2

    game_dir = args.game_dir or find_game_dir()
    vanilla = _vanilla_files(game_dir) if game_dir else set()

    # per-mod identifier indexes (exclude vanilla: cross-MOD collisions only)
    indexes = {str(d): index_mod(d) for d in args.mod}
    all_ids: dict[tuple[str, str], list[str]] = {}
    for mod_str, index in indexes.items():
        for kind, ids in index.items():
            for id_ in ids:
                all_ids.setdefault((kind, id_), []).append(mod_str)
    id_collisions = [
        {
            "kind": kind,
            "id": id_,
            "mods": mods,
            "definitions": [
                f"{m}:{f}:{ln}"
                for m in mods
                for f, ln in indexes[m][kind][id_]
            ],
        }
        for (kind, id_), mods in sorted(all_ids.items())
        if len(mods) > 1
    ]

    # vanilla shadows: a file shadowed by TWO OR MORE mods is a real
    # playset fight (load order decides); a single shadow is normal
    # full-file replacement and only informational
    shadow_map: dict[str, set[str]] = {}
    for d in args.mod:
        for path in d.glob("**/*"):
            if not path.is_file() or path.suffix not in (
                    ".txt", ".yml", ".yaml", ".gfx", ".gui"):
                continue
            rel = path.relative_to(d).as_posix()
            if rel in vanilla:
                shadow_map.setdefault(rel, set()).add(str(d))
    vanilla_shadows = [
        {"file": rel, "mods": sorted(mods)}
        for rel, mods in sorted(shadow_map.items())
        if len(mods) > 1
    ]

    # loc key collisions
    key_map: dict[str, set[str]] = {}
    for d in args.mod:
        for key, spots in _loc_keys(d).items():
            key_map.setdefault(key, set()).add(str(d))
    loc_collisions = [
        {"key": key, "mods": sorted(mods)}
        for key, mods in sorted(key_map.items())
        if len(mods) > 1
    ]

    result = {
        "mods": [str(d) for d in args.mod],
        "id_collisions": id_collisions,
        "vanilla_shadows": vanilla_shadows,
        "loc_collisions": loc_collisions,
    }

    conflicts = (len(id_collisions) + len(vanilla_shadows)
                 + len(loc_collisions))
    if args.json:
        print(json.dumps(result, indent=1))
    else:
        for c in id_collisions:
            print(f"[ID] {c['kind']} {c['id']}: {', '.join(c['mods'])}")
        for s in vanilla_shadows:
            print(f"[SHADOW] {s['file']}: {', '.join(s['mods'])}")
        for c in loc_collisions:
            print(f"[LOC] {c['key']}: {', '.join(c['mods'])}")
        print(f"\n{conflicts} conflict group(s) across {len(args.mod)} mods — "
              "playset load order decides the winner for file shadows")
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
