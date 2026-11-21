"""Eval harness: grade a mod directory against task-evals.json definitions.

Each eval entry: {name, mod_dir (gold or agent output), expect}. The
harness runs the validator and reports PASS/FAIL per eval — exit 1 on any
FAIL, so it gates CI/agents."""

import json
from pathlib import Path

from tools.run_evals import main

MINI = Path(__file__).parent / "fixtures" / "mini_mod"


def _write_evals(tmp_path: Path, evals: list[dict]) -> Path:
    p = tmp_path / "task-evals.json"
    p.write_text(json.dumps(evals), encoding="utf-8")
    return p


def test_all_pass_when_clean(tmp_path, capsys):
    # clean event file -> no errors, no warnings (with BOM loc absent means
    # missing-loc... keep expectations aligned with reality)
    mod = tmp_path / "out"
    (mod / "events").mkdir(parents=True)
    (mod / "events" / "ev.txt").write_text(
        'add_namespace = mymod\n'
        'country_event = {\n\tid = mymod.1\n\toption = {\n\t\tname = mymod.1.a\n\t}\n}\n',
        encoding="utf-8",
    )
    loc = mod / "localisation" / "english"
    loc.mkdir(parents=True)
    (loc / "m_l_english.yml").write_bytes(
        b'\xef\xbb\xbf' + b'l_english:\n mymod.1.a:0 "A"\n')
    evals = _write_evals(tmp_path, [
        {"name": "clean-event", "mod_dir": str(mod),
         "expect": {"max_errors": 0, "max_warnings": 0}},
    ])
    rc = main(["--evals", str(evals)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "PASS" in captured.out


def test_fail_when_rules_present(tmp_path, capsys):
    mod = tmp_path / "out"
    (mod / "events").mkdir(parents=True)
    (mod / "events" / "ev.txt").write_text(
        'country_event = {\n\tid = mymod.1\n}\n', encoding="utf-8")
    evals = _write_evals(tmp_path, [
        {"name": "no-duplicates-expected", "mod_dir": str(mod),
         "expect": {"forbidden_rules": ["missing-add-namespace"]}},
    ])
    rc = main(["--evals", str(evals)])
    captured = capsys.readouterr()
    assert rc == 1
    assert "FAIL" in captured.out


def test_self_test_mode_validates_gold(tmp_path):
    """--self-test runs every eval's mod_dir through its own expectations:
    the shipped gold solutions must pass their own gates."""
    mod = tmp_path / "gold"
    (mod / "events").mkdir(parents=True)
    (mod / "events" / "ev.txt").write_text(
        'add_namespace = mymod\ncountry_event = {\n\tid = mymod.1\n}\n',
        encoding="utf-8")
    evals = _write_evals(tmp_path, [
        {"name": "loose", "mod_dir": str(mod),
         "expect": {"max_errors": 0, "forbidden_rules": []}},
    ])
    rc = main(["--evals", str(evals), "--self-test"])
    assert rc == 0
