from pathlib import Path

import pytest

from tools.pdx_doc_parser import (
    DocEntry,
    GAME_DOC_FILES,
    parse_effects_or_triggers,
    parse_modifiers,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_effect_entry():
    entries = parse_effects_or_triggers(FIXTURES / "effects_sample.md", "effect")
    annex = next(e for e in entries if e.name == "annex_country")
    assert annex.kind == "effect"
    assert annex.scopes == ["COUNTRY"]
    assert annex.targets == ["THIS", "ROOT", "FROM"]
    assert "Annexes the specified country" in annex.description


def test_parse_trigger_entry():
    entries = parse_effects_or_triggers(FIXTURES / "triggers_sample.md", "trigger")
    assert len(entries) == 1
    trig = entries[0]
    assert trig.name == "has_idea"
    assert trig.kind == "trigger"
    assert trig.scopes == ["COUNTRY"]
    assert trig.targets == []
    assert "has_idea = war_economy" in trig.description


def test_entry_without_bullets():
    entries = parse_effects_or_triggers(FIXTURES / "effects_sample.md", "effect")
    tag = next(e for e in entries if e.name == "set_cosmetic_tag")
    assert tag.scopes == []
    assert tag.targets == []
    assert "no bullets" in tag.description


def test_headers_inside_code_fence_ignored():
    entries = parse_effects_or_triggers(FIXTURES / "effects_sample.md", "effect")
    tricky = next(e for e in entries if e.name == "tricky_entry")
    assert "## not_a_header" in tricky.description
    # no phantom entry was created from the line inside the fence
    assert all(e.name != "not_a_header" for e in entries)


def test_scope_section_headers_skipped():
    """`## Effects for scope COUNTRY` / Table of Content are sections, not entries."""
    entries = parse_effects_or_triggers(FIXTURES / "effects_sample.md", "effect")
    names = {e.name for e in entries}
    assert "annex_country" in names
    assert not any("for scope" in n for n in names)
    assert "Table of Content" not in names


def test_parse_modifiers_scopes():
    mods = parse_modifiers(FIXTURES / "modifiers_sample.md")
    assert set(mods.keys()) == {"country", "state"}
    assert "consumer_goods_factor" in mods["country"]
    assert "political_power_gain" in mods["country"]
    assert mods["state"] == ["local_resources"]


def test_templated_modifier_names():
    mods = parse_modifiers(FIXTURES / "modifiers_sample.md")
    # template names preserved verbatim and deduplicated
    assert mods["country"].count("<Building>_max_level_terrain_limit") == 1
    assert "<Building>_max_level_terrain_limit" in mods["country"]


def test_game_doc_files_mapping():
    assert GAME_DOC_FILES == {
        "effects_documentation": "effect",
        "triggers_documentation": "trigger",
    }


def test_crlf_and_bom(tmp_path):
    """Files with UTF-8 BOM and CRLF (Windows game output) parse identically."""
    src = FIXTURES / "effects_sample.md"
    text = src.read_text(encoding="utf-8")
    dest = tmp_path / "effects_sample.md"
    dest.write_bytes(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))
    entries = parse_effects_or_triggers(dest, "effect")
    annex = next(e for e in entries if e.name == "annex_country")
    assert annex.scopes == ["COUNTRY"]
    assert "Annexes the specified country" in annex.description
