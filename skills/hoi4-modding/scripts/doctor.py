"""Mod Doctor: one-shot health report combining the four audit tools.

Runs the validator, the identifier duplicate audit, the vanilla override
inventory and the localisation coverage report, writes a JSON report and
prints a verdict. The "Mod Doctor" concept from competitor review, built
entirely on this repo's tested tools.

Usage:
    python tools/doctor.py --mod <mod_dir> [--out report.json]
        [--game-dir <dir>] [--data <extracted_dir>] [--no-game]

Exit codes: 0 = healthy (no validator errors), 1 = findings, 2 = usage.
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
    from .validate import validate_mod
    from .find import duplicates, index_mod
    from .override_audit import audit_overrides
    from .loc_report import report as loc_report
except ImportError:
    from validate import validate_mod
    from find import duplicates, index_mod
    from override_audit import audit_overrides
    from loc_report import report as loc_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mod health report")
    parser.add_argument("--mod", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None, help="write JSON report")
    parser.add_argument("--game-dir", type=Path, default=None)
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--no-game", action="store_true")
    args = parser.parse_args(argv)

    if not args.mod.is_dir():
        print(f"error: {args.mod} is not a mod directory", file=sys.stderr)
        return 2
    game_dir = None if args.no_game else (args.game_dir or _auto_game())
    data_dir = args.data

    findings = validate_mod(args.mod, data_dir=data_dir, game_dir=game_dir)
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    index = index_mod(args.mod)
    dup_ids = duplicates(index)
    overrides = audit_overrides(args.mod, game_dir) if game_dir else []
    try:
        loc = loc_report(args.mod)
    except Exception:
        loc = {"english_keys": 0, "languages": {}}

    report = {
        "validator": {
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [
                {"severity": f.severity, "rule": f.rule, "file": f.file,
                 "line": f.line, "message": f.message}
                for f in findings
            ],
        },
        "duplicate_ids": [
            {"kind": d["kind"], "id": d["id"], "definitions": d["definitions"]}
            for d in dup_ids
        ],
        "vanilla_overrides": overrides,
        "loc_coverage": loc,
    }

    if args.out:
        args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False),
                            encoding="utf-8")

    print(f"Mod Doctor — {args.mod}")
    print(f"  validator : {len(errors)} error(s), {len(warnings)} warning(s)")
    print(f"  duplicate ids: {len(dup_ids)}")
    if game_dir:
        print(f"  vanilla overrides: {len(overrides)} file(s)")
    if loc.get("languages"):
        for lang, data in loc["languages"].items():
            print(f"  loc {lang:14s} missing {data['missing_count']}/{loc['english_keys']}")
    if args.out:
        print(f"  report: {args.out}")

    verdict = "healthy" if not errors and not dup_ids else "findings need attention"
    print(f"  verdict: {verdict}")
    return 0 if not errors and not dup_ids else 1


def _auto_game() -> Path | None:
    try:
        from .extract import find_game_dir
    except ImportError:
        from extract import find_game_dir
    return find_game_dir()


if __name__ == "__main__":
    raise SystemExit(main())
