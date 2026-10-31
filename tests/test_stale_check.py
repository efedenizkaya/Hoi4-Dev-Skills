"""stale_check: is the skill's verified game version still the installed
one? Mismatch -> suggest version_diff."""

from pathlib import Path

from tools.stale_check import main

FIXTURES = Path(__file__).parent / "fixtures"
FAKE_GAME = FIXTURES / "fake_game"
ROOT = Path(__file__).resolve().parents[1]


def test_match_exits_zero(capsys):
    rc = main(["--game-dir", str(FAKE_GAME)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "1.19.4.1" in out


def test_mismatch_exits_one(capsys, tmp_path):
    game = tmp_path / "game"
    game.mkdir()
    (game / "launcher-settings.json").write_text(
        json_dumps_raw("1.20.0"), encoding="utf-8")
    (game / "documentation").mkdir()
    rc = main(["--game-dir", str(game)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "1.20.0" in out and "version_diff" in out


def test_missing_launcher_exits_two(capsys, tmp_path):
    rc = main(["--game-dir", str(tmp_path)])
    captured = capsys.readouterr()
    assert rc == 2


def json_dumps_raw(version: str) -> str:
    import json

    return json.dumps({"rawVersion": version, "displayName": "Hearts of Iron IV"})
