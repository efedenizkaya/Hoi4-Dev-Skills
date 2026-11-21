"""Focus Tree Studio core: parse focus trees and analyze the graph.

Builds the prerequisite graph for every focus in a mod and reports:
- unreachable focuses (nothing can unlock them)
- prerequisite cycles
- critical path (longest chain, in points and days; FOCUS_POINT_DAYS = 7)
- broken prerequisite targets

Also renders a self-contained static HTML preview (grid layout + SVG
prerequisite lines, unreachable focuses highlighted). Analysis only —
never modifies mod files. The interactive drag-drop editor is out of
scope for this tool by design.

Usage:
    python tools/focus_map.py <mod_dir> [--json] [--html <out.html>]
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import html
import json
import re
import sys
from pathlib import Path

try:
    from .validate import (
        _FOCUS_DEF_RE,
        _FOCUS_ID_RE,
        _FOCUS_TARGET_RE,
        _extract_block,
        _read,
        mask_comments_and_strings,
    )
except ImportError:
    from validate import (
        _FOCUS_DEF_RE,
        _FOCUS_ID_RE,
        _FOCUS_TARGET_RE,
        _extract_block,
        _read,
        mask_comments_and_strings,
    )

FOCUS_POINT_DAYS = 7  # vanilla define (common/defines): 1 point = 1 week


def _collect_focuses(mod_dir: Path) -> list[dict]:
    """Every focus definition with id, cost, prereq targets, grid pos."""
    out: list[dict] = []
    for path in sorted(mod_dir.glob("common/national_focus/**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        for m in _FOCUS_DEF_RE.finditer(masked):
            end = _extract_block(masked, m.end() - 1)
            body = masked[m.end():end]
            id_m = _FOCUS_ID_RE.search(body)
            if not id_m:
                continue
            # grid x/y at the focus's own top level (offset blocks excluded)
            depth = 0
            pos: dict[str, str] = {}
            for km in re.finditer(r"([{}])|(?m:^[ \t]*)([xy])\s*=\s*(-?\d+)", body):
                if km.group(1):
                    depth += 1 if km.group(1) == "{" else -1
                    continue
                if depth == 0:
                    pos[km.group(2)] = km.group(3)
            prereqs = []
            for pm in re.finditer(r"prerequisite\s*=\s*\{([^{}]*)\}", body):
                prereqs.extend(_FOCUS_TARGET_RE.findall(pm.group(1)))
            out.append({
                "id": id_m.group(1),
                "cost": int(re.search(r"\bcost\s*=\s*(\d+)", body).group(1))
                if re.search(r"\bcost\s*=\s*(\d+)", body) else 0,
                "x": pos.get("x"),
                "y": pos.get("y"),
                "prereqs": prereqs,
                "file": rel,
                "line": masked.count("\n", 0, m.end() + id_m.start()) + 1,
            })
    return out


def build_graph(mod_dir: Path) -> dict:
    focuses = _collect_focuses(mod_dir)
    by_id = {f["id"]: f for f in focuses}
    edges = []
    broken_refs = []
    for f in focuses:
        for target in f["prereqs"]:
            edges.append({"from": target, "to": f["id"],
                          "file": f["file"], "line": f["line"]})
            if target not in by_id:
                broken_refs.append({"from": target, "to": f["id"],
                                    "file": f["file"]})

    # defined-node graph for reachability + cycles
    adj: dict[str, set[str]] = {fid: set() for fid in by_id}
    for e in edges:
        if e["from"] in by_id:
            adj[e["from"]].add(e["to"])

    roots = [fid for fid in adj if not by_id[fid]["prereqs"]]

    # reachability from roots
    reachable: set[str] = set()
    stack = list(roots)
    while stack:
        node = stack.pop()
        if node in reachable:
            continue
        reachable.add(node)
        stack.extend(adj.get(node, ()))

    unreachable = sorted(set(by_id) - reachable)

    # cycle detection (DFS over the defined graph, iterative)
    cycles: list[list[str]] = []
    state: dict[str, int] = {}
    for start in sorted(adj):
        if state.get(start):
            continue
        stack = [(start, iter(sorted(adj.get(start, ())))) ]
        path: list[str] = []
        on_path: set[str] = set()
        while stack:
            node, it = stack[-1]
            if state.get(node) != 1:
                state[node] = 1
                path.append(node)
                on_path.add(node)
            advanced = False
            for nxt in sorted(adj.get(node, ())):
                if state.get(nxt) == 1 and nxt in on_path:
                    cyc = path[path.index(nxt):]
                    cycles.append(cyc)
                elif not state.get(nxt):
                    state[nxt] = 1
                    stack.append((nxt, iter(sorted(adj.get(nxt, ())))))
                    path.append(nxt)
                    on_path.add(nxt)
                    advanced = True
                    break
            if not advanced:
                stack.pop()
                done = path.pop()
                on_path.discard(done)

    # critical path: longest chain by cost over the REACHABLE part
    # (unreachable focuses cannot be completed in game)
    best: dict[str, tuple[int, list[str]]] = {}

    def longest(node: str, seen: frozenset[str]) -> tuple[int, list[str]]:
        if node in best:
            return best[node]
        score, path = by_id[node]["cost"], [node]
        for nxt in sorted(adj.get(node, ())):
            # skip cycle members already on the current path; unreachable
            # focuses cannot be completed and are excluded from the graph
            if nxt in seen or nxt not in reachable:
                continue
            sub_score, sub_path = longest(nxt, seen | {node})
            if sub_score + by_id[node]["cost"] > score:
                score = sub_score + by_id[node]["cost"]
                path = [node] + sub_path
        best[node] = (score, path)
        return best[node]

    critical_path: list[str] = []
    critical_points = 0
    for node in sorted(reachable):
        if not by_id[node]["prereqs"]:  # roots
            score, path = longest(node, frozenset())
            if score > critical_points:
                critical_points, critical_path = score, path

    return {
        "focuses": focuses,
        "edges": edges,
        "broken_refs": broken_refs,
        "unreachable": [{"id": fid, "file": by_id[fid]["file"],
                         "line": by_id[fid]["line"]} for fid in unreachable],
        "cycles": cycles,
        "critical_path": critical_path,
        "critical_path_points": critical_points,
        "critical_path_days": critical_points * FOCUS_POINT_DAYS,
    }


def _html(graph: dict, mod_dir: Path) -> str:
    boxes = []
    lines = []
    for f in graph["focuses"]:
        x = int(f["x"]) * 120 + 20 if f["x"] is not None else 20
        y = int(f["y"]) * 80 + 20 if f["y"] is not None else 20
        unreach = any(u["id"] == f["id"] for u in graph["unreachable"])
        color = "#c0392b" if unreach else "#2980b9"
        boxes.append(
            f'<div class="focus" style="left:{x}px;top:{y}px;'
            f'border-color:{color}">{html.escape(str(f["id"]))}'
            f'<br><small>{html.escape(str(f["cost"]))} pts</small></div>')
    for e in graph["edges"]:
        src = next((f for f in graph["focuses"] if f["id"] == e["from"]), None)
        dst = next((f for f in graph["focuses"] if f["id"] == e["to"]), None)
        if src and dst and src["x"] is not None and dst["x"] is not None:
            x1 = int(src["x"]) * 120 + 110
            y1 = int(src["y"]) * 80 + 40
            x2 = int(dst["x"]) * 120 + 10
            y2 = int(dst["y"]) * 80 + 40
            lines.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="#7f8c8d" marker-end="url(#arrow)"/>')
    cp = " → ".join(graph["critical_path"]) or "(none)"
    unreach_ids = ", ".join(u["id"] for u in graph["unreachable"]) or "none"
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Focus map — {html.escape(mod_dir.name)}</title>
<style>
body {{ font-family: monospace; background: #1b1b1b; color: #ddd; }}
.focus {{ position: absolute; width: 100px; border: 2px solid; padding: 4px;
  background: #2c3e50; font-size: 11px; }}
svg {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; }}
.wrap {{ position: relative; height: 600px; }}
</style></head><body>
<h1>Focus map — {mod_dir.name}</h1>
<p>critical path: {html.escape(cp)} — {graph['critical_path_points']} pts
({graph['critical_path_days']} days)</p>
<p>unreachable: {html.escape(unreach_ids)}</p>
<p>cycles: {len(graph['cycles'])} · broken prereq refs: {len(graph['broken_refs'])}</p>
<svg width="1400" height="600"><defs><marker id="arrow" markerWidth="8"
markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6"
fill="#7f8c8d"/></marker></defs>{''.join(lines)}</svg>
<div class="wrap">{''.join(boxes)}</div>
</body></html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Focus tree graph analysis")
    parser.add_argument("mod_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--html", type=Path, default=None,
                        help="write a self-contained HTML preview")
    args = parser.parse_args(argv)

    if not args.mod_dir.is_dir():
        print(f"error: {args.mod_dir} is not a mod directory", file=sys.stderr)
        return 2

    graph = build_graph(args.mod_dir)

    if args.json:
        print(json.dumps(graph, indent=1))
        return 0

    print(f"focuses: {len(graph['focuses'])}")
    print(f"prerequisite edges: {len(graph['edges'])}")
    print(f"unreachable: {len(graph['unreachable'])}")
    print(f"cycles: {len(graph['cycles'])}")
    print(f"broken prereq refs: {len(graph['broken_refs'])}")
    print(f"critical path: {' -> '.join(graph['critical_path']) or '(none)'} — "
          f"{graph['critical_path_points']} pts / "
          f"{graph['critical_path_days']} days")

    if args.html:
        args.html.write_text(_html(graph, args.mod_dir), encoding="utf-8")
        print(f"html preview: {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
