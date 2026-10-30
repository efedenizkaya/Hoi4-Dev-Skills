"""Identifier indexer (find.py): the 'searcher' workflows of competitor
skills, as one tool — id -> file:line across mod + vanilla."""

import json
from pathlib import Path

from tools.find import index_mod, main

FIXTURES = Path(__file__).parent / "fixtures"
MINI_MOD = FIXTURES / "mini_mod"
FAKE_GAME = FIXTURES / "fake_game"


def test_index_events_focuses_and_scripted(tmp_path):
    (MINI_MOD / "common" / "scripted_effects").mkdir(parents=True, exist_ok=True)
    (MINI_MOD / "common" / "scripted_effects" / "helpers.txt").write_text(
        "ger_test_helper = {\n\tadd_stability = 0.01\n}\n", encoding="utf-8"
    )
    try:
        index = index_mod(MINI_MOD)
        assert "ger_test.1" in index["event"]
        assert "ger_test.2" in index["event"]
        assert index["event"]["ger_test.1"][0][0].endswith("events_a.txt")
        assert "test_focus" in index["focus"]
        assert "ger_test_helper" in index["scripted_effect"]
    finally:
        (MINI_MOD / "common" / "scripted_effects" / "helpers.txt").unlink()


def test_index_includes_vanilla_with_game_dir(tmp_path):
    index = index_mod(MINI_MOD, game_dir=FAKE_GAME)
    # fake_game declares ger_test.3 as an event
    assert "ger_test.3" in index["event"]
    # and vanilla_focus_1 as a focus
    assert "vanilla_focus_1" in index["focus"]


def test_duplicates_report(tmp_path):
    (MINI_MOD / "events" / "dup.txt").write_text(
        "add_namespace = mymod\ncountry_event = {\n\tid = ger_test.1\n}\n",
        encoding="utf-8",
    )
    try:
        index = index_mod(MINI_MOD)
        dups = {k: v for k, v in index["event"].items() if len(v) > 1}
        assert "ger_test.1" in dups
        assert len(dups["ger_test.1"]) == 2
    finally:
        (MINI_MOD / "events" / "dup.txt").unlink()


def test_cli_lookup_and_json(capsys, tmp_path):
    rc = main(["ger_test", "--mod", str(MINI_MOD), "--game-dir", str(FAKE_GAME),
               "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    matches = [e for e in data["matches"] if "ger_test" in e["id"]]
    assert matches, data
    assert {"kind", "id", "file", "line"} <= set(matches[0])
    assert rc == 0


def test_cli_no_match_exits_1(capsys):
    rc = main(["no_such_identifier_xyz", "--mod", str(MINI_MOD)])
    assert rc == 1
