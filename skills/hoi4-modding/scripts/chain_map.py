"""Event chain map: which events fire which.

Parses the mod's event files and builds the firing graph — every
`country_event = { id = X }` (and siblings) fired from inside an event
definition becomes an edge `defining_event -> fired_id`. Chains, cycles
and dangling targets become visible instead of buried in 7000-line files.

Usage:
    python tools/chain_map.py <mod_dir> [--json]
        [--namespace mymod] [--show-undefined]

Exit codes: 0 = ok, 2 = usage error.
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
    from .validate import (
        _brace_depth_at,
        _event_ids_in,
        _EVENT_HEADER_RE,
        mask_comments_and_strings,
        _read,
    )
except ImportError:
    from validate import (
        _brace_depth_at,
        _event_ids_in,
        _EVENT_HEADER_RE,
        mask_comments_and_strings,
        _read,
    )


def build_graph(mod_dir: Path) -> dict:
    """Returns {events_defined, edges: [{from, to, file, line}],
    undefined_targets: sorted unique ids with no definition in the mod}."""
    defined: set[str] = set()
    edges: list[dict] = []

    for path in sorted(mod_dir.glob("events/**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        current = None  # the event definition we are inside, if any
        for m in _EVENT_HEADER_RE.finditer(masked):
            inside = _brace_depth_at(masked, m.start()) > 0
            ids = _event_ids_in(masked, m)
            if not inside:
                if ids:
                    current = ids[0][0]
                    defined.add(current)
                continue
            for ref_id, line in ids:
                edges.append(
                    {"from": current, "to": ref_id, "file": rel, "line": line}
                )

    undefined = sorted({e["to"] for e in edges} - defined)
    return {
        "events_defined": len(defined),
        "edges": edges,
        "undefined_targets": undefined,
        "defined": sorted(defined),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Event firing graph")
    parser.add_argument("mod_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--namespace", default=None,
                        help="only show edges from this namespace")
    parser.add_argument("--show-undefined", action="store_true",
                        help="highlight edges to events not defined in the mod")
    args = parser.parse_args(argv)

    if not args.mod_dir.is_dir():
        print(f"error: {args.mod_dir} is not a mod directory", file=sys.stderr)
        return 2

    graph = build_graph(args.mod_dir)
    edges = graph["edges"]
    if args.namespace:
        edges = [e for e in edges if e["from"].startswith(args.namespace)]

    if args.json:
        out = dict(graph, edges=edges)
        print(json.dumps(out, indent=1))
        return 0

    print(f"events defined: {graph['events_defined']}")
    print(f"edges: {len(edges)}")
    for e in edges:
        mark = ""
        if args.show_undefined and e["to"] in graph["undefined_targets"]:
            mark = "  [UNDEFINED]"
        print(f"  {e['from']} -> {e['to']}  ({e['file']}:{e['line']}){mark}")
    if args.show_undefined:
        und = graph["undefined_targets"]
        print(f"\nundefined targets: {len(und)}" + (f": {', '.join(und)}" if und else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
