"""Balance Lab core: static per-country strength extraction.

Parses `history/states/*.txt` (ownership, buildings, manpower) and
`history/countries/*.txt` (capital, starting ideas) into a comparative
per-country report (JSON or markdown).

This is a STATIC 1936-build snapshot: it does not simulate focus rewards,
decisions, trades or gameplay. Balance judgment stays with the agent and
the user.

Usage:
    python tools/balance_lab.py --mod <mod_dir> [--json] [--out report.md]
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from .validate import _extract_block, _read, mask_comments_and_strings
except ImportError:
    from validate import _extract_block, _read, mask_comments_and_strings

BUILDING_KEYS = ("industrial_complex", "arms_factory", "dockyard")


def _latest_block(body: str, header_re: re.Pattern) -> str | None:
    """Content of the LAST matching `header = { ... }` block (later blocks
    override earlier ones in HOI4 history files)."""
    last = None
    for m in header_re.finditer(body):
        end = _extract_block(body, m.end() - 1)
        last = body[m.end():end]
    return last


_BUILDINGS_RE = re.compile(r"\bbuildings\s*=\s*\{")
_OWNER_RE = re.compile(r"\bowner\s*=\s*([A-Z][A-Z0-9]{2})")
_ID_HEADER_RE = re.compile(r"\bid\s*=\s*(\d+)")
_MANPOWER_RE = re.compile(r"\bmanpower\s*=\s*(\d+)")
_ADD_IDEAS_RE = re.compile(r"\badd_ideas\s*=\s*([A-Za-z0-9_.]+)")
_CAPITAL_RE = re.compile(r"\bcapital\s*=\s*(\d+)")


def _scan_states(root: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(root.glob("history/states/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        id_m = _ID_HEADER_RE.search(masked)
        if not id_m:
            continue
        body = _latest_block(masked, re.compile(r"\bhistory\s*=\s*\{")) or ""
        owner_m = _OWNER_RE.search(body)
        if not owner_m:
            continue
        tag = owner_m.group(1)
        buildings = {}
        b_m = _latest_block(body, _BUILDINGS_RE)
        if b_m:
            for key in BUILDING_KEYS:
                bm = re.search(rf"\b{key}\s*=\s*(\d+)", b_m)
                if bm:
                    buildings[key] = int(bm.group(1))
        mp = _MANPOWER_RE.search(masked)
        entry = out.setdefault(tag, {
            "states": 0, "civilian_factories": 0, "military_factories": 0,
            "dockyards": 0, "manpower": 0, "state_ids": [],
        })
        entry["states"] += 1
        entry["state_ids"].append(int(id_m.group(1)))
        key_map = {"industrial_complex": "civilian_factories",
                   "arms_factory": "military_factories",
                   "dockyard": "dockyards"}
        for key in BUILDING_KEYS:
            entry[key_map[key]] += buildings.get(key, 0)
        if mp:
            entry["manpower"] += int(mp.group(1))
    return out


def _scan_countries(root: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(root.glob("history/countries/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        tag_m = re.match(r"([A-Z][A-Z0-9]{2})", path.name)
        if not tag_m:
            continue
        tag = tag_m.group(1)
        cap = _CAPITAL_RE.search(masked)
        ideas = [m.group(1) for m in _ADD_IDEAS_RE.finditer(masked)]
        entry = out.setdefault(tag, {"capital": None, "starting_ideas": []})
        if cap:
            entry["capital"] = int(cap.group(1))
        entry["starting_ideas"].extend(ideas)
    return out


def build_report(mod_dir: Path) -> dict:
    states = _scan_states(mod_dir)
    countries = _scan_countries(mod_dir)
    tags = sorted(set(states) | set(countries))
    out = []
    for tag in tags:
        s = states.get(tag, {})
        c = countries.get(tag, {})
        out.append({
            "tag": tag,
            "states": s.get("states", 0),
            "civilian_factories": s.get("civilian_factories", 0),
            "military_factories": s.get("military_factories", 0),
            "dockyards": s.get("dockyards", 0),
            "manpower": s.get("manpower", 0),
            "capital": c.get("capital"),
            "starting_ideas": c.get("starting_ideas", []),
        })
    return {"countries": out, "note": (
        "static build snapshot from history files; does not simulate "
        "focuses, decisions, trades or gameplay")}


def _markdown(report: dict) -> str:
    lines = ["# Balance Lab — comparative strength (static snapshot)", "",
             f"{len(report['countries'])} countries", "",
             "| Tag | States | Civ factories | Mil factories | Dockyards | "
             "Manpower | Capital | Starting ideas |",
             "|---|---|---|---|---|---|---|---|"]
    for c in sorted(report["countries"], key=lambda x: -x["manpower"]):
        lines.append(
            f"| {c['tag']} | {c['states']} | {c['civilian_factories']} | "
            f"{c['military_factories']} | {c['dockyards']} | "
            f"{c['manpower']:,} | {c['capital']} | "
            f"{', '.join(c['starting_ideas']) or '-'} |")
    lines.append("")
    lines.append("_" + report["note"] + "_")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Balance Lab core")
    parser.add_argument("--mod", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    if not (args.mod / "history").is_dir():
        print(f"error: {args.mod} has no history/ folder", file=sys.stderr)
        return 2

    report = build_report(args.mod)
    if args.out:
        if args.out.suffix == ".json":
            args.out.write_text(json.dumps(report, indent=1), encoding="utf-8")
        else:
            args.out.write_text(_markdown(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=1))
        return 0

    print(_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
