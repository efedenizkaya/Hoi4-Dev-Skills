"""Identifier indexer for HOI4 mods: the "searcher" workflow as one tool.

Indexes every defined identifier (events, focuses, ideas, decisions,
scripted effects/triggers, characters) in a mod and — with the game dir —
the vanilla definitions too, then answers "where is X defined?" with
file:line evidence, and reports duplicates.

Usage:
    python tools/find.py <pattern> [--mod <dir>] [--game-dir <dir>]
                        [--kind event|focus|...] [--json] [--duplicates]

Pattern is a substring match on ids; use --duplicates to list ids defined
more than once.
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

try:  # sibling import inside the skill bundle
    from .validate import (
        _EVENT_HEADER_RE,
        _FOCUS_DEF_RE,
        _event_ids_in,
        mask_comments_and_strings,
        _read,
        _extract_block,
        _top_level_names,
    )
except ImportError:  # repo-root / direct script run
    from validate import (
        _EVENT_HEADER_RE,
        _FOCUS_DEF_RE,
        _event_ids_in,
        mask_comments_and_strings,
        _read,
        _extract_block,
        _top_level_names,
    )


def _index_events(path: Path, masked: str, out: dict[str, list]) -> None:
    rel = str(path)
    depth = 0
    last = 0
    for m in _EVENT_HEADER_RE.finditer(masked):
        depth += masked.count("{", last, m.start()) - masked.count("}", last, m.start())
        last = m.start()
        if depth > 0:
            continue
        for event_id, line in _event_ids_in(masked, m):
            out.setdefault(event_id, []).append((rel, line))


def _index_focuses(path: Path, masked: str, out: dict[str, list]) -> None:
    rel = str(path)
    for m in _FOCUS_DEF_RE.finditer(masked):
        end = _extract_block(masked, m.end() - 1)
        body = masked[m.end():end]
        id_m = re.search(r"\bid\s*=\s*([\w.\-]+)", body)
        if id_m:
            line = masked.count("\n", 0, m.end() + id_m.start()) + 1
            out.setdefault(id_m.group(1), []).append((rel, line))


def _index_depth1_names(path: Path, masked: str, out: dict[str, list],
                        under: str | None = None) -> None:
    """Names at depth 0 of the file, or — when `under` is given — depth 1
    inside that wrapper block (e.g. `characters = { <names> }`)."""
    rel = str(path)
    if under:
        m = re.search(rf"\b{under}\s*=\s*\{{", masked)
        if not m:
            return
        end = _extract_block(masked, m.end() - 1)
        masked = masked[m.end():end]
    stmt_re = re.compile(r"([{}])|(?m:^)(\s*)([a-z0-9_]+)(?=\s*=)")
    depth = 0
    for m in stmt_re.finditer(masked):
        if m.group(1):
            depth += 1 if m.group(1) == "{" else -1
            continue
        if depth != 0:
            continue
        name = m.group(3)
        line = masked.count("\n", 0, m.start()) + 1
        out.setdefault(name, []).append((rel, line))


def index_mod(mod_dir: Path, game_dir: Path | None = None) -> dict[str, dict[str, list]]:
    """Index defined identifiers. Returns kind -> id -> [(file, line), ...].

    Kinds: event, focus, idea, decision, decision_category, scripted_effect,
    scripted_trigger, character.
    """
    index: dict[str, dict[str, list]] = {
        "event": {}, "focus": {}, "idea": {}, "decision": {},
        "decision_category": {}, "scripted_effect": {},
        "scripted_trigger": {}, "character": {},
    }

    def scan(root: Path) -> None:
        for path in sorted(root.glob("events/**/*.txt")):
            _index_events(path, mask_comments_and_strings(_read(path)), index["event"])
        for path in sorted(root.glob("common/national_focus/**/*.txt")):
            _index_focuses(path, mask_comments_and_strings(_read(path)), index["focus"])
        for path in sorted(root.glob("common/scripted_effects/**/*.txt")):
            for name in _top_level_names(path):
                index["scripted_effect"].setdefault(name, []).append((str(path), 0))
        for path in sorted(root.glob("common/scripted_triggers/**/*.txt")):
            for name in _top_level_names(path):
                index["scripted_trigger"].setdefault(name, []).append((str(path), 0))
        for path in sorted(root.glob("common/decisions/categories/**/*.txt")):
            for name in _top_level_names(path):
                index["decision_category"].setdefault(name, []).append((str(path), 0))
        for path in sorted(root.glob("common/decisions/**/*.txt")):
            if "categories" in path.parts:
                continue
            for name in _top_level_names(path):
                index["decision"].setdefault(name, []).append((str(path), 0))
        for path in sorted(root.glob("common/characters/*.txt")):
            masked = mask_comments_and_strings(_read(path))
            _index_depth1_names(path, masked, index["character"], under="characters")

    scan(mod_dir)
    if game_dir is not None:
        scan(game_dir)
    return index


def lookup(index: dict[str, dict[str, list]], pattern: str) -> list[dict]:
    matches = []
    for kind, ids in index.items():
        for id_, spots in ids.items():
            if pattern.lower() in id_.lower():
                for file, line in spots:
                    matches.append({"kind": kind, "id": id_, "file": file, "line": line})
    return sorted(matches, key=lambda m: (m["kind"], m["id"], m["file"]))


def duplicates(index: dict[str, dict[str, list]]) -> list[dict]:
    out = []
    for kind, ids in index.items():
        for id_, spots in ids.items():
            if len(spots) > 1:
                out.append({"kind": kind, "id": id_,
                            "definitions": [f"{f}:{l}" for f, l in spots]})
    return sorted(out, key=lambda d: (d["kind"], d["id"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HOI4 identifier indexer")
    parser.add_argument("pattern", nargs="?", default="")
    parser.add_argument("--mod", type=Path, default=Path("."))
    parser.add_argument("--game-dir", type=Path, default=None)
    parser.add_argument("--kind", default=None,
                        help="filter: event|focus|idea|decision|...")
    parser.add_argument("--duplicates", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--record", type=str, default=None, metavar="NAME",
        help="print the full official record (description, scopes) for one "
             "effect/trigger/modifier NAME from the extracted database",
    )
    parser.add_argument(
        "--data", type=Path, default=None,
        help="extracted dir for --record (default: ../extracted relative to cwd)")

    args = parser.parse_args(argv)

    if args.record:
        data_dir = args.data or Path("extracted/1.19.4.1")
        if not data_dir.is_dir():
            print(f"error: no extracted data at {data_dir} — run "
                  "scripts/extract.py first (or pass --data)", file=sys.stderr)
            return 2
        record = None
        for kind, fname in (("effect", "effects.json"), ("trigger", "triggers.json")):
            for e in json.loads((data_dir / fname).read_text(encoding="utf-8")):
                if e["name"] == args.record:
                    record = {"kind": kind, **e}
                    break
            if record:
                break
        else:
            for scope, names in json.loads(
                    (data_dir / "modifiers.json").read_text(encoding="utf-8")).items():
                if args.record in names:
                    record = {"kind": "modifier", "name": args.record, "scope": scope}
                    break
        if record is None:
            print(f"error: '{args.record}' not found in the extracted database",
                  file=sys.stderr)
            return 1
        print(json.dumps(record, indent=1, ensure_ascii=False))
        return 0

    index = index_mod(args.mod, args.game_dir)
    if args.kind:
        index = {k: v for k, v in index.items() if k == args.kind}

    if args.duplicates:
        dups = duplicates(index)
        if args.json:
            print(json.dumps(dups, indent=1))
        else:
            for d in dups:
                print(f"[{d['kind']}] {d['id']}: {', '.join(d['definitions'])}")
            print(f"\n{len(dups)} duplicate identifier(s)")
        return 0 if not dups else 1

    matches = lookup(index, args.pattern)
    if args.json:
        print(json.dumps({"matches": matches}, indent=1))
        return 0 if matches else 1
    for m in matches:
        print(f"[{m['kind']}] {m['id']}  {m['file']}:{m['line']}")
    print(f"\n{len(matches)} match(es)")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
