import re
from pathlib import Path

import pytest
from tools.validate import Finding, validate_mod

FIXTURES = Path(__file__).parent / "fixtures"
MINI_MOD = FIXTURES / "mini_mod"
FAKE_GAME = FIXTURES / "fake_game"


def _find(findings: list[Finding], rule: str) -> list[Finding]:
    return [f for f in findings if f.rule == rule]


def test_braces_in_comments_and_strings():
    """Braces in comments and quoted strings must not count as unbalanced."""
    findings = validate_mod(MINI_MOD)
    ideas = MINI_MOD / "common" / "ideas" / "quotes_in_strings.txt"
    hits = [f for f in findings if str(ideas.name) in f.file]
    assert hits == []


def test_unbalanced_braces_detected():
    findings = validate_mod(MINI_MOD)
    hits = _find(findings, "unbalanced-braces")
    assert len(hits) == 1
    assert hits[0].severity == "error"
    assert "broken_braces.txt" in hits[0].file


def test_duplicate_event_id_across_files():
    findings = validate_mod(MINI_MOD)
    hits = _find(findings, "duplicate-event-id")
    assert len(hits) == 1
    assert hits[0].message.startswith("ger_test.2")
    assert hits[0].severity == "error"


def test_missing_loc_key():
    findings = validate_mod(MINI_MOD)
    hits = _find(findings, "missing-loc-key")
    assert all("ger_test.2" not in f.message for f in hits)  # keys exist
    assert hits == []  # fixture events all have keys present


def test_missing_loc_key_detected(tmp_path):
    """A loc ref pointing nowhere is reported."""
    (tmp_path / "events").mkdir()
    (tmp_path / "events" / "ev.txt").write_text(
        'country_event = {\n\tid = mymod.1\n\ttitle = mymod.1.t\n\tdesc = mymod.1.d\n\n\toption = {\n\t\tname = mymod.1.a\n\t}\n}\n',
        encoding="utf-8",
    )
    (tmp_path / "localisation").mkdir()
    findings = validate_mod(tmp_path)
    hits = _find(findings, "missing-loc-key")
    assert {f.message.split(":")[0] for f in hits} == {
        "mymod.1.t",
        "mymod.1.d",
        "mymod.1.a",
    }
    assert all(f.severity == "error" for f in hits)


def test_loc_encoding_warning():
    findings = validate_mod(MINI_MOD)
    hits = _find(findings, "loc-file-encoding")
    assert len(hits) == 1
    assert "bad_l_english.yml" in hits[0].file
    assert hits[0].severity == "warning"


def test_clean_mod_no_findings():
    """The fixture yields exactly its three intentional findings, no more."""
    findings = validate_mod(MINI_MOD)
    assert sorted(f.rule for f in findings) == [
        "duplicate-event-id",
        "loc-file-encoding",
        "unbalanced-braces",
    ]


def test_vanilla_loc_suppressed_with_game_dir():
    """Loc keys defined by the base game must not be flagged when the game
    dir is known (mods commonly copy vanilla events)."""
    events = MINI_MOD / "events"
    extra = events / "zz_vanilla_copy.txt"
    extra.write_text(
        "country_event = {\n"
        "\tid = ger_test.4\n"
        "\ttitle = vanilla.3.t\n"
        "\tdesc = vanilla.3.d\n"
        "\toption = { name = vanilla.3.a }\n"
        "}\n",
        encoding="utf-8",
    )
    try:
        without = validate_mod(MINI_MOD)
        assert any("vanilla.3.t" in f.message for f in without)
        with_game = validate_mod(MINI_MOD, game_dir=FAKE_GAME)
        assert not any("vanilla.3" in f.message for f in with_game)
    finally:
        extra.unlink()


def test_vanilla_event_override_is_warning():
    """Redefining an existing vanilla event ID once is an intentional
    override — warning, not error. Defining it twice in the mod stays an
    error."""
    events = MINI_MOD / "events"
    override = events / "zz_override.txt"
    override.write_text(
        "country_event = {\n"
        "\tid = ger_test.3\n"
        "\ttitle = vanilla.3.t\n"
        "\tdesc = vanilla.3.d\n"
        "\toption = { name = vanilla.3.a }\n"
        "}\n",
        encoding="utf-8",
    )
    try:
        findings = validate_mod(MINI_MOD, game_dir=FAKE_GAME)
        hits = _find(findings, "vanilla-event-override")
        assert len(hits) == 1
        assert hits[0].severity == "warning"
        assert "ger_test.3" in hits[0].message
        # twice in the mod remains a hard error
        assert any(
            f.rule == "duplicate-event-id" and "ger_test.2" in f.message
            for f in findings
        )
    finally:
        override.unlink()


def test_paired_strings_produce_no_quote_finding(tmp_path):
    """Strings closed on later lines must not count as unbalanced quotes —
    masking has to blank BOTH quote chars of a string."""
    (tmp_path / "events").mkdir()
    (tmp_path / "events" / "strings.txt").write_text(
        'a = "first string"\n'
        'b = "second string"\n'
        'c = "string with # hash"\n',
        encoding="utf-8",
    )
    findings = validate_mod(tmp_path)
    assert not _find(findings, "unbalanced-quotes")


def test_genuinely_odd_quotes_detected(tmp_path):
    (tmp_path / "events").mkdir()
    (tmp_path / "events" / "odd.txt").write_text(
        'a = "unclosed string\nb = 2\n',
        encoding="utf-8",
    )
    findings = validate_mod(tmp_path)
    hits = _find(findings, "unbalanced-quotes")
    assert len(hits) == 1
    assert hits[0].severity == "error"


def test_nonexistent_mod_path_exits_2(capsys, tmp_path):
    """A mistyped mod path must never read as a clean bill of health."""
    from tools.validate import main

    rc = main([str(tmp_path / "does_not_exist")])
    captured = capsys.readouterr()
    assert rc == 2
    assert "not a mod directory" in captured.err


def test_exit_code_error(capsys):
    from tools.validate import main

    rc = main([str(MINI_MOD)])
    captured = capsys.readouterr()
    assert rc == 1
    assert "unbalanced-braces" in captured.out
