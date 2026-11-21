"""Mod Architect core: project memory (JSON) + consistency checker.

The architect tracks the mod's scenario — countries, characters, timeline
entries, content registry and relations — and detects contradictions:
events before a participant's birth, one-way alliances, undefined
dependencies, participants that are not defined countries."""

import json
from pathlib import Path

import pytest

from tools.architect import main


def _init(tmp_path: Path, extra_args: list[str] | None = None) -> Path:
    proj = tmp_path / "architect.json"
    args = ["init", "--name", "Test Mod", "--project", str(proj)] + (extra_args or [])
    rc = main(args)
    assert rc == 0
    return proj


def _load(proj: Path) -> dict:
    return json.loads(proj.read_text(encoding="utf-8"))


def test_init_creates_schema(tmp_path):
    proj = _init(tmp_path)
    d = _load(proj)
    assert d["name"] == "Test Mod"
    assert d["countries"] == [] and d["characters"] == []
    assert d["timeline"] == [] and d["content"] == [] and d["relations"] == []


def test_add_country_and_character(tmp_path):
    proj = _init(tmp_path)
    main(["add-country", "GER", "--project", str(proj),
          "--name", "Germany", "--ideology", "fascism",
          "--government", "Nazi dictatorship"])
    main(["add-character", "GER_leader", "--project", str(proj),
          "--name", "Kurt", "--country", "GER", "--born", "1890.1.1",
          "--roles", "country_leader,advisor"])
    d = _load(proj)
    assert d["countries"][0]["tag"] == "GER"
    assert d["characters"][0]["born"] == "1890.1.1"
    assert "advisor" in d["characters"][0]["roles"]


def test_timeline_entry_with_participants(tmp_path):
    proj = _init(tmp_path)
    main(["add-country", "GER", "--project", str(proj)])
    main(["add-country", "POL", "--project", str(proj)])
    main(["add-timeline", "--project", str(proj), "--date", "1939.9.1",
          "--title", "Invasion of Poland", "--participants", "GER,POL"])
    d = _load(proj)
    assert d["timeline"][0]["participants"] == ["GER", "POL"]


def test_check_clean_project_passes(tmp_path):
    proj = _init(tmp_path)
    main(["add-country", "GER", "--project", str(proj)])
    rc = main(["check", "--project", str(proj)])
    assert rc == 0


def test_check_event_before_birth(tmp_path, capsys):
    proj = _init(tmp_path)
    main(["add-character", "old_leader", "--project", str(proj),
          "--name", "Old Leader", "--country", "GER", "--born", "1890.1.1"])
    main(["add-timeline", "--project", str(proj), "--date", "1850.1.1",
          "--title", "Too early", "--participants", "old_leader"])
    rc = main(["check", "--project", str(proj)])
    assert rc == 1
    # the text finding names the rule and both dates
    out = capsys.readouterr().out
    assert "[event-before-birth]" in out
    assert "1890.1.1" in out and "1850.1.1" in out


def test_check_finds_birth_contradiction_in_report(tmp_path):
    proj = _init(tmp_path)
    main(["add-character", "old_leader", "--project", str(proj),
          "--name", "Old Leader", "--country", "GER", "--born", "1890.1.1"])
    main(["add-timeline", "--project", str(proj), "--date", "1850.1.1",
          "--title", "Too early", "--participants", "old_leader"])
    main(["check", "--project", str(proj), "--json", "--out",
          str(tmp_path / "report.json")])
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    rules = [f["rule"] for f in report["findings"]]
    assert "event-before-birth" in rules


def test_check_one_way_alliance(tmp_path):
    proj = _init(tmp_path)
    main(["add-country", "GER", "--project", str(proj)])
    main(["add-country", "POL", "--project", str(proj)])
    main(["add-relation", "GER", "--project", str(proj), "--allies", "POL"])
    main(["check", "--project", str(proj), "--json", "--out",
          str(tmp_path / "r.json")])
    report = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    rules = [f["rule"] for f in report["findings"]]
    assert "one-way-relation" in rules


def test_check_undefined_participant(tmp_path):
    proj = _init(tmp_path)
    main(["add-timeline", "--project", str(proj), "--date", "1936.1.1",
          "--title", "Mystery summit", "--participants", "ZZZ"])
    main(["check", "--project", str(proj), "--json", "--out",
          str(tmp_path / "r.json")])
    report = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    rules = [f["rule"] for f in report["findings"]]
    assert "undefined-participant" in rules


def test_check_reports_corrupt_project_as_usage_error(tmp_path, capsys):
    proj = _init(tmp_path)
    proj.write_text("{ not json", encoding="utf-8")
    # _load reports usage errors via SystemExit(2) — the CLI contract
    with pytest.raises(SystemExit) as exc_info:
        main(["check", "--project", str(proj)])
    assert exc_info.value.code == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_add_character_rejects_impossible_date(tmp_path, capsys):
    proj = _init(tmp_path)
    rc = main(["add-character", "old_leader", "--project", str(proj),
               "--name", "Old Leader", "--country", "GER", "--born", "1890.13.1"])
    assert rc == 2
    assert "month/day out of range" in capsys.readouterr().err
    assert json.loads(proj.read_text(encoding="utf-8"))["characters"] == []


def test_add_timeline_rejects_malformed_date(tmp_path, capsys):
    proj = _init(tmp_path)
    rc = main(["add-timeline", "--project", str(proj), "--date", "not-a-date",
               "--title", "Too early", "--participants", "GER"])
    assert rc == 2
    assert "expected YYYY.M.D" in capsys.readouterr().err


def test_init_rejects_bad_timeline_start(tmp_path, capsys):
    proj = tmp_path / "p.json"
    rc = main(["init", "--name", "Test Mod", "--project", str(proj),
               "--timeline-start", "1936.99.1"])
    assert rc == 2
    assert "month/day out of range" in capsys.readouterr().err
    assert not proj.exists()


def test_check_undefined_content_dependency(tmp_path):
    proj = _init(tmp_path)
    main(["add-content", "focus", "mymod_branch", "--project", str(proj),
          "--depends", "mymod_missing_focus"])
    main(["check", "--project", str(proj), "--json", "--out",
          str(tmp_path / "r.json")])
    report = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    rules = [f["rule"] for f in report["findings"]]
    assert "undefined-dependency" in rules
