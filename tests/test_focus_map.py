"""Focus Tree Studio core: parse focus trees, prerequisite graph,
unreachable/cycle detection, critical-path duration, JSON + HTML output."""

import json
from pathlib import Path

from tools.focus_map import build_graph, main

TREE = Path(__file__).parent / "fixtures" / "focus_map_mod"


def test_definitions_and_edges():
    graph = build_graph(TREE)
    ids = {f["id"] for f in graph["focuses"]}
    assert ids == {"mymod_rearm", "mymod_economy", "mymod_industry",
                   "mymod_ghost_dep", "mymod_cycled_a", "mymod_cycled_b"}
    edges = {(e["from"], e["to"]) for e in graph["edges"]}
    # prerequisite = { focus = A focus = B } inside mymod_industry
    assert ("mymod_rearm", "mymod_industry") in edges
    assert ("mymod_economy", "mymod_industry") in edges
    assert ("mymod_ghost_dep", "mymod_cycled_a") in edges


def test_unreachable_detection():
    graph = build_graph(TREE)
    # mymod_cycled_a/b depend on each other (cycle) and on a ghost dep:
    # nothing reaches them from a root
    unreachable = {f["id"] for f in graph["unreachable"]}
    assert {"mymod_cycled_a", "mymod_cycled_b",
            "mymod_ghost_dep"} <= unreachable
    assert "mymod_rearm" not in unreachable


def test_cycle_detection():
    graph = build_graph(TREE)
    cycles = graph["cycles"]
    assert any(set(c) == {"mymod_cycled_a", "mymod_cycled_b"} for c in cycles)


def test_critical_path_duration():
    graph = build_graph(TREE)
    # mymod_rearm(5) + mymod_industry(15) = 20 points = 140 days (x7)
    assert graph["critical_path_points"] == 21
    assert graph["critical_path_days"] == 147
    assert set(graph["critical_path"]) == {"mymod_economy", "mymod_industry"}


def test_json_output(capsys):
    rc = main([str(TREE), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["focuses"] and data["edges"]
    assert rc == 0


def test_html_output(tmp_path):
    out = tmp_path / "tree.html"
    rc = main([str(TREE), "--html", str(out)])
    assert rc == 0
    html = out.read_text(encoding="utf-8")
    assert "mymod_industry" in html          # boxes rendered
    assert "unreachable" in html.lower()     # flagged visually
    assert "147" in html                     # critical path days


def test_missing_dir_exits_two(capsys):
    rc = main([str(Path(__file__).parent / "nope")])
    capsys.readouterr()  # swallow the error text; rc is the contract
    assert rc == 2
