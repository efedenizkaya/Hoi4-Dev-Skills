"""chain_map: map which events fire which — the trigger graph of a mod."""

import json
from pathlib import Path

from tools.chain_map import build_graph, main

MOD = Path(__file__).parent / "fixtures" / "chain_mod"


def test_graph_edges(tmp_path):
    graph = build_graph(MOD)
    edges = {(e["from"], e["to"]) for e in graph["edges"]}
    assert ("mymod.1", "mymod.2") in edges          # chained via option
    assert ("mymod.2", "mymod.3") in edges          # chained via immediate
    assert ("mymod.4", "ghost.9") in edges          # fires an undefined event
    assert all(e["file"].endswith(".txt") for e in graph["edges"])


def test_undefined_targets_listed(tmp_path):
    graph = build_graph(MOD)
    assert "ghost.9" in graph["undefined_targets"]
    assert "mymod.2" not in graph["undefined_targets"]


def test_cli_json(capsys):
    rc = main([str(MOD), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["events_defined"] == 4
    assert len(data["edges"]) == 3
    assert rc == 0
