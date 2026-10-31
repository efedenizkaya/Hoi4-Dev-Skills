"""Inventory the mod's full-file vanilla overrides.

A mod file with the same relative path as a vanilla file REPLACES it
entirely — the classic source of "my mod breaks after a patch" (the patch
changes the vanilla file, the stale mod copy wins). This tool lists every
exact shadow, so the maintainer can decide which ones must be refreshed or
made additive.

Usage:
    python tools/override_audit.py --mod <mod_dir> --game-dir <game_dir> [--json]

Exit codes: 0 = no exact overrides, 1 = overrides found, 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _vanilla_files(game_dir: Path) -> set[str]:
    """Relative paths of vanilla content files (script + loc + interface)."""
    out: set[str] = set()
    for top in ("common", "events", "history", "interface", "localisation"):
        root = game_dir / top
        if not root.is_dir():
            continue
        for path in root.glob("**/*"):
            if path.is_file() and path.suffix in (".txt", ".yml", ".yaml", ".gfx", ".gui"):
                out.add(path.relative_to(game_dir).as_posix())
    return out


def audit_overrides(mod_dir: Path, game_dir: Path) -> list[dict]:
    """Report every mod file that exactly shadows a vanilla file."""
    vanilla = _vanilla_files(game_dir)
    report: list[dict] = []
    for path in sorted(mod_dir.glob("**/*")):
        if not path.is_file() or path.suffix not in (".txt", ".yml", ".yaml", ".gfx", ".gui"):
            continue
        rel = path.relative_to(mod_dir).as_posix()
        if rel in vanilla:
            report.append({"kind": "exact-replace", "file": rel})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory vanilla file overrides")
    parser.add_argument("--mod", type=Path, required=True)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    for label, d in (("--mod", args.mod), ("--game-dir", args.game_dir)):
        if not d.is_dir():
            print(f"error: {label} {d} is not a directory", file=sys.stderr)
            return 2

    report = audit_overrides(args.mod, args.game_dir)
    if args.json:
        print(json.dumps(report, indent=1))
    else:
        for r in report:
            print(f"[{r['kind']}] {r['file']}")
        print(
            f"\n{len(report)} exact vanilla override(s) — each one must be "
            "refreshed whenever the patch changes the vanilla file"
        )
    return 1 if report else 0


if __name__ == "__main__":
    raise SystemExit(main())
