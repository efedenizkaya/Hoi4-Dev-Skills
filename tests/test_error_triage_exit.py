"""error_triage exit codes and clean-log deltas (from the owner audit)."""

from pathlib import Path

from tools.error_triage import LogError, diff, main

FIX = Path(__file__).parent / "fixtures"


def test_positive_delta_exits_1(capsys):
    before = FIX / "error_before.log"
    after = FIX / "error_after.log"  # has +2 net new errors vs before
    rc = main([str(after), "--against", str(before)])
    assert rc == 1


def test_negative_delta_exits_0(capsys, tmp_path):
    baseline = FIX / "error_before.log"
    better = tmp_path / "better.log"
    text = baseline.read_text(encoding="utf-8").replace(
        "set_technology: Invalid tech\n", "", 1
    )  # one invalid-tech fixed, everything else unchanged
    better.write_text(text, encoding="utf-8")
    rc = main([str(better), "--against", str(baseline)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "invalid-tech" in captured.out and "-1" in captured.out


def test_clean_current_log_with_dirty_baseline_shows_delta(capsys, tmp_path):
    clean = tmp_path / "clean.log"
    clean.write_text(
        "[10:00:00][no_game_date]: startup fine\n", encoding="utf-8"
    )
    dirty = FIX / "error_after.log"
    rc = main([str(clean), "--against", str(dirty)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "invalid-scope" in captured.out  # classes shown as fixed
