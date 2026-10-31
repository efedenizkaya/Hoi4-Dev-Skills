"""Vanilla-override audit: which mod files shadow vanilla files exactly
(full-file-replace risk). Fostanico's audit-vanilla-overrides idea, as a
tested stdlib tool."""

import json
from pathlib import Path

from tools.override_audit import audit_overrides, main

FIXTURES = Path(__file__).parent / "fixtures"
FAKE_GAME = FIXTURES / "fake_game"


def test_audit_finds_exact_shadow(tmp_path):
    # mod file that shadows a vanilla file
    (tmp_path / "common" / "ideas").mkdir(parents=True)
    (tmp_path / "common" / "ideas" / "_economic.txt").write_text(
        "idea = {}\n", encoding="utf-8"
    )
    # mod file that does NOT shadow anything
    (tmp_path / "common" / "ideas" / "mymod_ideas.txt").write_text(
        "idea = {}\n", encoding="utf-8"
    )
    report = audit_overrides(tmp_path, FAKE_GAME)
    shadowed = [r for r in report if r["kind"] == "exact-replace"]
    assert any("_economic.txt" in r["file"] for r in shadowed)
    assert not any("mymod_ideas.txt" in r["file"] for r in shadowed)


def test_audit_ignores_vanilla_only_files(tmp_path):
    report = audit_overrides(tmp_path, FAKE_GAME)
    assert report == []  # empty mod shadows nothing


def test_cli_json_and_exit(capsys, tmp_path):
    (tmp_path / "events").mkdir(parents=True)
    (tmp_path / "events" / "vanilla_events.txt").write_text(
        "country_event = { id = x.1 }\n", encoding="utf-8"
    )
    rc = main(["--mod", str(tmp_path), "--game-dir", str(FAKE_GAME), "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert any("vanilla_events.txt" in r["file"] for r in data)
    assert rc == 1  # shadowing present -> exit 1 so agents/CI notice
