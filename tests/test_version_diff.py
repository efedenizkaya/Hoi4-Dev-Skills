"""Version diff: compare two extracted game-data dirs — the migration
workflow for new HOI4 patches."""

import json
from pathlib import Path

from tools.version_diff import diff_versions, main


def _write_extracted(root: Path, version: str, effects: list[str],
                     triggers: list[str], modifiers: dict) -> Path:
    d = root / version
    d.mkdir(parents=True)
    (d / "effects.json").write_text(json.dumps(
        [{"name": n, "kind": "effect", "scopes": [], "targets": [],
          "description": ""} for n in effects]), encoding="utf-8")
    (d / "triggers.json").write_text(json.dumps(
        [{"name": n, "kind": "trigger", "scopes": [], "targets": [],
          "description": ""} for n in triggers]), encoding="utf-8")
    (d / "modifiers.json").write_text(json.dumps(modifiers), encoding="utf-8")
    return d


def test_diff_versions_added_removed(tmp_path):
    old = _write_extracted(tmp_path, "1.19.4",
                           ["annex_country", "add_stability"],
                           ["has_idea"], {"country": ["pp_gain", "old_mod"]})
    new = _write_extracted(tmp_path, "1.20.0",
                           ["annex_country", "add_stability", "new_effect"],
                           ["has_idea", "new_trigger"],
                           {"country": ["pp_gain", "new_mod"], "state": ["local_res"]})
    result = diff_versions(old, new)
    assert result["effects"]["added"] == ["new_effect"]
    assert result["effects"]["removed"] == []
    assert result["triggers"]["added"] == ["new_trigger"]
    assert result["modifiers"]["added"] == {"country": ["new_mod"], "state": ["local_res"]}
    assert result["modifiers"]["removed"] == {"country": ["old_mod"]}


def test_cli_summary_and_exit(capsys, tmp_path):
    old = _write_extracted(tmp_path, "1.19.4", ["a"], ["b"], {})
    new = _write_extracted(tmp_path, "1.20.0", ["a", "c"], ["b"], {})
    rc = main([str(old), str(new)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "new_effect" in out or "+1" in out


def test_missing_dir_exits_2(capsys, tmp_path):
    rc = main([str(tmp_path / "nope"), str(tmp_path / "nope2")])
    captured = capsys.readouterr()
    assert rc == 2
    assert "extract" in captured.err.lower()


def _write_effect(root: Path, version: str, name: str, scopes: list[str],
                  desc: str) -> None:
    d = root / version
    d.mkdir(parents=True, exist_ok=True)
    recs = []
    existing = d / "effects.json"
    if existing.is_file():
        recs = json.loads(existing.read_text(encoding="utf-8"))
    recs = [r for r in recs if r["name"] != name]
    recs.append({"name": name, "kind": "effect", "scopes": scopes,
                 "targets": [], "description": desc})
    existing.write_text(json.dumps(recs, indent=1), encoding="utf-8")


def test_changed_record_detected(tmp_path):
    """Same name, changed scope/description -> 'changed' with field diffs."""
    old = _write_extracted(tmp_path, "1.19.4", ["effect_x"], ["b"], {})
    _write_effect(tmp_path, "1.19.4", "effect_x", ["country"],
                  "old description")
    new = _write_extracted(tmp_path, "1.20.0", ["effect_x"], ["state"], {})
    _write_effect(tmp_path, "1.20.0", "effect_x", ["state"],
                  "new description")
    result = diff_versions(old, new)
    ch = result["effects"].get("changed", [])
    assert len(ch) == 1 and ch[0]["name"] == "effect_x"
    fields = ch[0]["fields"]
    assert fields["scopes"] == {"old": ["country"], "new": ["state"]}
    assert fields["description"] == {"old": "old description",
                                     "new": "new description"}


def test_unchanged_record_not_listed(tmp_path):
    old = _write_extracted(tmp_path, "1.19.4", ["effect_x"], ["b"], {})
    _write_effect(tmp_path, "1.19.4", "effect_x", ["country"],
                  "old description")
    new = _write_extracted(tmp_path, "1.20.0", ["effect_x"], ["b"], {})
    _write_effect(tmp_path, "1.20.0", "effect_x", ["country"],
                  "old description")
    result = diff_versions(old, new)
    assert result["effects"].get("changed", []) == []
    assert result["effects"]["added"] == [] and result["effects"]["removed"] == []
