import json
from pathlib import Path

import pytest

from tools.extract import extract, find_game_dir

FIXTURES = Path(__file__).parent / "fixtures"
FAKE_GAME = FIXTURES / "fake_game"


def test_version_read_from_launcher_settings(tmp_path):
    out = tmp_path / "extracted"
    data_dir = extract(FAKE_GAME, out)
    assert data_dir.name == "1.19.4.1"


def test_extract_writes_versioned_json(tmp_path):
    out = tmp_path / "extracted"
    data_dir = extract(FAKE_GAME, out)
    effects = json.loads((data_dir / "effects.json").read_text(encoding="utf-8"))
    triggers = json.loads((data_dir / "triggers.json").read_text(encoding="utf-8"))
    modifiers = json.loads((data_dir / "modifiers.json").read_text(encoding="utf-8"))
    assert effects[0]["kind"] == "effect"
    assert effects[0]["name"] == "annex_country"
    assert effects[0]["scopes"] == ["COUNTRY"]
    assert triggers[0]["name"] == "has_idea"
    assert "country" in modifiers
    assert "consumer_goods_factor" in modifiers["country"]


def test_summary_counts(tmp_path):
    out = tmp_path / "extracted"
    extract(FAKE_GAME, out, summary_out=tmp_path / "summary.json")
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert summary["gameVersion"] == "1.19.4.1"
    assert summary["counts"]["effects"] == 4  # 4 entries in effects_sample.md
    assert summary["counts"]["triggers"] == 1
    assert summary["counts"]["modifiers"]["country"] == 3


def test_cli_summary_out_flag(capsys, tmp_path):
    """The documented CLI flow `--summary-out <f>` must succeed and leave
    both the custom summary and the data-dir summary.json in place."""
    from tools.extract import main

    out = tmp_path / "extracted"
    summary = tmp_path / "summary.json"
    rc = main(
        [
            "--game-dir",
            str(FAKE_GAME),
            "--out",
            str(out),
            "--summary-out",
            str(summary),
        ]
    )
    assert rc == 0
    assert summary.is_file()
    assert (out / "1.19.4.1" / "summary.json").is_file()
    assert "game version" in capsys.readouterr().out


def test_cli_missing_documentation_exits_2(capsys, tmp_path):
    from tools.extract import main

    bare = tmp_path / "bare_game"
    bare.mkdir()
    (bare / "launcher-settings.json").write_text('{"rawVersion": "1.0.0"}')
    rc = main(["--game-dir", str(bare), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert "documentation" in capsys.readouterr().err


def test_auto_detect_game_dir(monkeypatch, tmp_path):
    # explicit env var wins
    monkeypatch.setenv("HOI4_GAME_DIR", str(FAKE_GAME))
    assert find_game_dir() == FAKE_GAME.resolve()

    # default Steam path when it exists
    steam_path = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
    monkeypatch.delenv("HOI4_GAME_DIR")
    if steam_path.is_dir():
        assert find_game_dir() == steam_path
    else:
        assert find_game_dir() is None

    # nothing found -> None
    monkeypatch.setenv("HOI4_GAME_DIR", "")
    monkeypatch.setattr(Path, "is_dir", lambda self: False)
    assert find_game_dir() is None


def test_extract_rejects_missing_documentation(tmp_path):
    empty = tmp_path / "not_a_game"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        extract(empty, tmp_path / "out")
