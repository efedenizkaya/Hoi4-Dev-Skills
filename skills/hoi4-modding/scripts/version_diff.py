"""Compare two extracted game-data directories (from tools/extract.py).

The migration workflow for a new HOI4 patch: extract the new version, diff
against the stored old one, and see exactly which effects/triggers/modifiers
appeared, disappeared, or changed — then re-verify the claims register.

Usage:
    python tools/version_diff.py <old_extracted_dir> <new_extracted_dir> [--json]
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import json
import sys
from pathlib import Path


def _load(d: Path, name: str):
    p = d / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def diff_versions(old_dir: Path, new_dir: Path) -> dict:
    result: dict = {}
    for kind in ("effects", "triggers"):
        old = {e["name"] for e in (_load(old_dir, f"{kind}.json") or [])}
        new = {e["name"] for e in (_load(new_dir, f"{kind}.json") or [])}
        result[kind] = {"added": sorted(new - old), "removed": sorted(old - new)}

    old_m = _load(old_dir, "modifiers.json") or {}
    new_m = _load(new_dir, "modifiers.json") or {}
    mod_added, mod_removed = {}, {}
    for scope in set(old_m) | set(new_m):
        added = sorted(set(new_m.get(scope, [])) - set(old_m.get(scope, [])))
        removed = sorted(set(old_m.get(scope, [])) - set(new_m.get(scope, [])))
        if added:
            mod_added[scope] = added
        if removed:
            mod_removed[scope] = removed
    result["modifiers"] = {"added": mod_added, "removed": mod_removed}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diff two extracted game versions")
    parser.add_argument("old_dir", type=Path)
    parser.add_argument("new_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    for d in (args.old_dir, args.new_dir):
        if not (d / "effects.json").is_file():
            print(
                f"error: {d} is not an extracted data dir (no effects.json) — "
                "run scripts/extract.py per version first",
                file=sys.stderr,
            )
            return 2

    result = diff_versions(args.old_dir, args.new_dir)
    if args.json:
        print(json.dumps(result, indent=1))
        return 0

    total_new = sum(len(v["added"]) for k, v in result.items() if k != "modifiers")
    total_gone = sum(len(v["removed"]) for k, v in result.items() if k != "modifiers")
    print(f"effects : +{len(result['effects']['added'])} -{len(result['effects']['removed'])}")
    print(f"triggers: +{len(result['triggers']['added'])} -{len(result['triggers']['removed'])}")
    mod_added_n = sum(len(v) for v in result["modifiers"]["added"].values())
    mod_removed_n = sum(len(v) for v in result["modifiers"]["removed"].values())
    print(f"modifiers: +{mod_added_n} -{mod_removed_n}")
    for kind in ("effects", "triggers"):
        if result[kind]["added"]:
            print(f"\nnew {kind}: {', '.join(result[kind]['added'])}")
        if result[kind]["removed"]:
            print(f"removed {kind}: {', '.join(result[kind]['removed'])}")
    print(
        f"\nnet: +{total_new} -{total_gone} script entries — "
        "re-verify claims-register rows tagged with the old version"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
