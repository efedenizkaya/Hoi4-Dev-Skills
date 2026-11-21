"""loc_report: per-language localisation coverage — which keys exist in
english but are missing from other language folders."""

import json
from pathlib import Path

from tools.loc_report import main, report


def _make_mod(tmp_path: Path) -> Path:
    loc = tmp_path / "localisation"
    def lang(name, keys):
        d = loc / name
        d.mkdir(parents=True)
        body = "l_english:\n" if name == "english" else f"l_{name}:\n"
        for k in keys:
            body += f" {k}:0 \"x\"\n"
        (d / f"mod_l_{name}.yml").write_bytes(
            b"\xef\xbb\xbf" + body.encode("utf-8"))
    lang("english", ["shared_key", "event_1_t", "event_2_t", "english_only"])
    lang("german", ["shared_key", "event_1_t"])           # missing event_2_t, english_only
    lang("simp_chinese", ["shared_key"])                  # missing 3
    return tmp_path


def test_report_counts_missing_per_language(tmp_path):
    mod = _make_mod(tmp_path)
    result = report(mod)
    assert set(result["languages"]) == {"german", "simp_chinese"}
    assert result["english_keys"] == 4
    ger = result["languages"]["german"]
    assert ger["missing_count"] == 2
    assert "event_2_t" in ger["missing"]
    assert "english_only" in ger["missing"]
    assert result["languages"]["simp_chinese"]["missing_count"] == 3


def test_cli_runs_and_exits_zero(capsys, tmp_path):
    mod = _make_mod(tmp_path)
    rc = main(["--mod", str(mod), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["english_keys"] == 4
    assert rc == 0


def test_mod_without_english_exits_2(capsys, tmp_path):
    (tmp_path / "localisation" / "german").mkdir(parents=True)
    rc = main(["--mod", str(tmp_path)])
    assert rc == 2
