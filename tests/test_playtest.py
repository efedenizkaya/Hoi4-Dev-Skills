"""Playtester: structured test definitions + evaluation of game-run
evidence. The USER launches HOI4 — this tool prepares the run (pre-checks
+ checklist) and evaluates the resulting error.log diff against
expectations. It never launches the game and never accepts "game started"
as a passing test."""

import json
from pathlib import Path

from tools.playtest import main

FIX = Path(__file__).parent / "fixtures"
MINI = Path(__file__).parent / "fixtures" / "mini_mod"

TESTS = {
    "tests": [
        {
            "id": "spirit-grant",
            "mod_dir": str(MINI),
            "description": "Completing a focus grants the correct spirit",
            "expect": {"max_errors": 2},
        },
        {
            "id": "loc-clean",
            "mod_dir": str(MINI),
            "description": "No missing localisation findings remain",
            "expect": {"forbidden_rules": ["missing-loc-key"]},
        },
    ]
}


def _write_tests(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "playtests.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_precheck_reports_per_test(capsys, tmp_path):
    # MINI is the intentionally broken fixture: pre-check fails (rc 1) but
    # the in-game checklist is still printed for each test
    p = _write_tests(tmp_path, TESTS)
    rc = main(["run", "--tests", str(p)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "spirit-grant" in out and "loc-clean" in out
    assert "PRE-CHECK FAILED" in out
    assert "checklist" in out.lower()  # in-game steps are printed


def test_evaluate_pass_on_clean_diff(capsys, tmp_path):
    before = FIX / "error_before.log"
    # error_after has +2 net new errors vs before, so a passing diff needs
    # a CLEAN after-log; build one from the baseline
    clean = tmp_path / "clean_after.log"
    lines = before.read_text(encoding="utf-8").splitlines()
    clean.write_text("\n".join(lines[3:]) + "\n", encoding="utf-8")  # drop 4
    p = _write_tests(tmp_path, [
        {"id": "clean-run", "mod_dir": str(MINI),
         "expect": {"max_new_errors": 0}}])
    rc = main(["evaluate", "--tests", str(p), "--id", "clean-run",
               "--baseline", str(before), "--after", str(clean),
               "--results", str(tmp_path / "results.json")])
    data = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    entry = next(r for r in data if r["id"] == "clean-run")
    assert entry["pass"] is True
    assert rc == 0


def test_evaluate_fail_on_new_errors(tmp_path):
    before = FIX / "error_before.log"
    after = FIX / "error_after.log"  # net +2 new errors
    p = _write_tests(tmp_path, [
        {"id": "regression-run", "mod_dir": str(MINI),
         "expect": {"max_new_errors": 0}}])
    rc = main(["evaluate", "--tests", str(p), "--id", "regression-run",
               "--baseline", str(before), "--after", str(after),
               "--results", str(tmp_path / "results.json")])
    data = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    entry = next(r for r in data if r["id"] == "regression-run")
    assert entry["pass"] is False
    assert entry["new_errors"] == 2
    assert rc == 1


def test_results_file_written(tmp_path):
    p = _write_tests(tmp_path, [TESTS["tests"][0]])
    out = tmp_path / "results.json"
    main(["evaluate", "--tests", str(p), "--baseline",
          str(FIX / "error_before.log"), "--after",
          str(FIX / "error_before.log"), "--results", str(out)])
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data[0]["pass"] is True
