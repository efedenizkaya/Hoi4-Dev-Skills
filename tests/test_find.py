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


def test_character_line_numbers_are_real():
    """Regression: line numbers were computed on the TRUNCATED text after
    the `characters = {` wrapper, so every character reported line 1."""
    index = index_mod(MINI_MOD, game_dir=FAKE_GAME)
    # FAKE_GAME has no characters dir; use the kit example directly
    kit = (Path(__file__).resolve().parents[1] / "skills" / "hoi4-modding"
           / "assets" / "kits" / "characters-kit")
    index = index_mod(kit)
    spots = index["character"]["mymod_leader"]
    assert len(spots) == 1
    file, line = spots[0]
    text = (kit / "common" / "characters" / "mymod_characters.txt").read_text(
        encoding="utf-8").splitlines()
    assert "mymod_leader" in text[line - 1], f"line {line} not on id line"


def test_scripted_effect_lines_are_real(tmp_path):
    d = tmp_path / "common" / "scripted_effects"
    d.mkdir(parents=True)
    (d / "helpers.txt").write_text(
        "# top comment\n\nmy_helper = {\n\tadd_stability = 0.1\n}\n",
        encoding="utf-8")
    index = index_mod(tmp_path)
    spots = index["scripted_effect"]["my_helper"]
    file, line = spots[0]
    assert line == 3, spots


def _extracted(root: Path) -> Path:
    data = root / "extracted" / "1.19.5.0"
    data.mkdir(parents=True)
    (data / "effects.json").write_text(json.dumps([
        {"name": "annex_country", "kind": "effect",
         "description": f"record in {data.name}",
         "scopes": ["COUNTRY"], "targets": ["THIS"]}]), encoding="utf-8")
    (data / "triggers.json").write_text("[]", encoding="utf-8")
    (data / "modifiers.json").write_text("{}", encoding="utf-8")
    return data


def test_record_reads_named_effect(tmp_path, capsys):
    data = _extracted(tmp_path)
    rc = main(["--record", "annex_country", "--data", str(data)])
    out = capsys.readouterr().out
    assert rc == 0
    assert '"name": "annex_country"' in out and '"kind": "effect"' in out


def test_record_defaults_to_newest_extracted(tmp_path, monkeypatch, capsys):
    """The default --record data dir must follow the newest extracted
    version, not a hardcoded stale one."""
    old = _extracted(tmp_path).parent.parent / "1.19.4.1"
    old.mkdir(parents=True)
    (old / "effects.json").write_text(json.dumps([
        {"name": "annex_country", "kind": "effect", "description": "old",
         "scopes": [], "targets": []}]), encoding="utf-8")
    (old / "triggers.json").write_text("[]", encoding="utf-8")
    (old / "modifiers.json").write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    rc = main(["--record", "annex_country"])
    assert rc == 0
    assert "record in 1.19.5.0" in capsys.readouterr().out


def test_record_missing_data_exits_2(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no extracted/ here
    rc = main(["--record", "annex_country"])
    assert rc == 2
    assert "no extracted data" in capsys.readouterr().err
