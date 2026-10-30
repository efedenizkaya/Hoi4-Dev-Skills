from pathlib import Path

from tools.error_triage import classify, diff, main, parse_log

FIXTURES = Path(__file__).parent / "fixtures"
BEFORE = FIXTURES / "error_before.log"
AFTER = FIXTURES / "error_after.log"


def test_parse_line_format():
    errors = parse_log(BEFORE)
    assert len(errors) == 8
    first = errors[0]
    assert first.time == "18:53:57"
    assert first.date == "1936.01.01.12"
    assert first.source == "database_scoped_variables.cpp:267"
    assert first.message.startswith("invalid database object")


def test_classification_buckets():
    errors = parse_log(BEFORE)
    buckets = classify(errors)
    assert len(buckets["invalid-database-object"]) == 3
    assert len(buckets["invalid-tech"]) == 1
    assert len(buckets["invalid-scope"]) == 2
    assert len(buckets["loc-error"]) == 1
    assert len(buckets["other"]) == 1


def test_diff_groups_repeats():
    """Identical repeated errors count as one class; only real changes move
    the delta. Digit-only differences (line numbers) must not split groups."""
    before = parse_log(BEFORE)
    after = parse_log(AFTER)
    delta = diff(before, after)
    # the three invalid-database-object errors persist unchanged -> 0
    assert delta["invalid-database-object"] == 0
    # one extra "Invalid tech" line was added
    assert delta["invalid-tech"] == 1
    # one extra set_character_flag error (same message, different line)
    assert delta["invalid-scope"] == 1
    # the loc error was fixed
    assert delta["loc-error"] == -1
    # recruit_character error persists
    assert delta["other"] == 0


def test_cli_runs_on_fixture(capsys):
    rc = main([str(AFTER), "--against", str(BEFORE)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "invalid-tech" in out
    assert "+1" in out
    assert "loc-error" in out and "-1" in out
