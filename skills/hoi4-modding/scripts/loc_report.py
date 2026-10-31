"""Localisation coverage report: which keys exist in the mod's english
files but are missing from other language folders.

Useful for multi-language mods (the game falls back to english, so missing
translations are silent). Key sets are compared per language folder; the
base-game languages are english, german, french, spanish, russian, polish,
braz_por, japanese, simp_chinese.

Usage:
    python tools/loc_report.py --mod <mod_dir> [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_LOC_KEY_RE = re.compile(r"^\s*([A-Za-z][\w.\-]*):\d*\s*\"", re.M)


def _keys_in(folder: Path) -> set[str]:
    keys: set[str] = set()
    if not folder.is_dir():
        return keys
    for path in folder.glob("**/*.yml"):
        keys.update(_LOC_KEY_RE.findall(
            path.read_text(encoding="utf-8-sig", errors="replace")))
    return keys


def report(mod_dir: Path) -> dict:
    loc = mod_dir / "localisation"
    languages = [d.name for d in loc.iterdir() if d.is_dir()] if loc.is_dir() else []
    english = _keys_in(loc / "english")
    result: dict = {"english_keys": len(english), "languages": {}}
    for lang in sorted(l for l in languages if l != "english"):
        missing = sorted(english - _keys_in(loc / lang))
        result["languages"][lang] = {
            "missing_count": len(missing),
            "missing": missing,
        }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Localisation coverage report")
    parser.add_argument("--mod", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if not (args.mod / "localisation" / "english").is_dir():
        print(
            "error: no localisation/english folder — english is the "
            "coverage baseline",
            file=sys.stderr,
        )
        return 2

    result = report(args.mod)
    if args.json:
        print(json.dumps(result, indent=1))
        return 0

    print(f"english keys: {result['english_keys']}")
    for lang, data in result["languages"].items():
        print(f"{lang:16s} missing {data['missing_count']}/{result['english_keys']}")
        for key in data["missing"][:10]:
            print(f"    {key}")
        if data["missing_count"] > 10:
            print(f"    … and {data['missing_count'] - 10} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
