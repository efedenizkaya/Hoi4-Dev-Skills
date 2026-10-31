"""Audit-fix tests round 3: offset blocks must not corrupt x/y reading,
desc-block loc refs, and localisation file hygiene rules."""

from pathlib import Path

from tools.validate import validate_mod

FIXTURES = Path(__file__).parent / "fixtures"
FAKE_GAME = FIXTURES / "fake_game"


def test_offset_block_does_not_corrupt_grid_position(tmp_path):
    """`offset = { x = -25 y = 0 }` is a conditional pixel nudge; the focus
    grid x/y must come from the focus itself (regression: findall took the
    LAST x/y, so offset values overwrote the grid position)."""
    (tmp_path / "common" / "national_focus").mkdir(parents=True)
    (tmp_path / "common" / "national_focus" / "tree.txt").write_text(
        "focus_tree = {\n"
        "\tfocus = {\n"
        "\t\tid = mod_offset_a\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 1\n"
        "\t\ty = 0\n"
        "\t\tcost = 5\n"
        "\t\toffset = {\n"
        "\t\t\tx = -25\n"
        "\t\t\ty = 0\n"
        "\t\t\ttrigger = { has_game_rule = { rule = obsolete_focus_branches_visibility option = HIDE } }\n"
        "\t\t}\n"
        "\t}\n"
        "\tfocus = {\n"
        "\t\tid = mod_offset_b\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 1\n"
        "\t\ty = 0\n"
        "\t\tcost = 5\n"
        "\t}\n"
        "}\n",
        encoding="utf-8",
    )
    findings = validate_mod(tmp_path)
    # grid positions are both (1, 0) -> genuine overlap warning; but the
    # buggy reader saw (-25, 0) vs (1, 0) and MISSED it
    hits = [f for f in findings if f.rule == "focus-position-overlap"]
    assert len(hits) == 1
    assert "mod_offset_a" in hits[0].message


def test_desc_block_loc_refs_checked(tmp_path):
    """`desc = { text = key trigger = {...} }` refs must be loc-checked
    (512 uses in vanilla events)."""
    (tmp_path / "events").mkdir()
    (tmp_path / "events" / "ev.txt").write_text(
        "add_namespace = mymod\n"
        "country_event = {\n"
        "\tid = mymod.1\n"
        "\ttitle = mymod.1.t\n"
        "\tdesc = {\n"
        "\t\ttext = mymod.1.d\n"
        "\t\ttrigger = { always = yes }\n"
        "\t}\n"
        "\toption = {\n"
        "\t\tname = mymod.1.a\n"
        "\t}\n"
        "}\n",
        encoding="utf-8",
    )
    findings = validate_mod(tmp_path)
    hits = [f for f in findings if f.rule == "missing-loc-key"]
    assert {f.message.split(":")[0] for f in hits} == {
        "mymod.1.t", "mymod.1.d", "mymod.1.a",
    }


def test_loc_language_header_mismatch(tmp_path):
    """A file in the german folder with an l_english header is flagged."""
    loc = tmp_path / "localisation" / "german"
    loc.mkdir(parents=True)
    (loc / "mod_l_german.yml").write_bytes(
        b"\xef\xbb\xbf" + b"l_english:\n some.key:0 \"x\"\n")
    findings = validate_mod(tmp_path)
    hits = [f for f in findings if f.rule == "loc-language-mismatch"]
    assert len(hits) == 1


def test_duplicate_loc_key(tmp_path):
    loc = tmp_path / "localisation" / "english"
    loc.mkdir(parents=True)
    (loc / "mod_l_english.yml").write_bytes(
        b"\xef\xbb\xbf" +
        b"l_english:\n dup.key:0 \"a\"\n dup.key:0 \"b\"\n")
    findings = validate_mod(tmp_path)
    hits = [f for f in findings if f.rule == "duplicate-loc-key"]
    assert len(hits) == 1