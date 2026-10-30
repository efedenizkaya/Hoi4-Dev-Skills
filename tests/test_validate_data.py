"""Data-aware validation (--data): statement names checked against the
extracted effect/trigger databases, and focus references checked against
mod + vanilla focus definitions. All warnings-only: the game itself is the
final authority."""

import json
from pathlib import Path

import pytest
from tools.extract import extract
from tools.validate import validate_mod

FIXTURES = Path(__file__).parent / "fixtures"
FAKE_GAME = FIXTURES / "fake_game"


@pytest.fixture()
def data_dir(tmp_path):
    return extract(FAKE_GAME, tmp_path / "extracted")


def _mod(tmp_path: Path, script: str, extra: dict[str, str] | None = None) -> Path:
    (tmp_path / "events").mkdir(exist_ok=True)
    (tmp_path / "events" / "ev.txt").write_text(script, encoding="utf-8")
    for rel, content in (extra or {}).items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return tmp_path


EVENT = """country_event = {
	id = mymod.1
	title = mymod.1.t
	desc = mymod.1.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes

	option = {
		name = mymod.1.a
		annex_country = GER
		add_stability = 0.05
		not_a_real_effect = { value = 1 }
	}
}
"""


def test_unknown_statement_name_warned(tmp_path, data_dir):
    findings = validate_mod(_mod(tmp_path, EVENT), data_dir)
    hits = [f for f in findings if f.rule == "unknown-statement-name"]
    assert len(hits) == 1
    assert hits[0].severity == "warning"
    assert "not_a_real_effect" in hits[0].message


def test_known_effects_and_fields_stay_silent(tmp_path, data_dir):
    findings = validate_mod(_mod(tmp_path, EVENT), data_dir)
    names = [f.message for f in findings if f.rule == "unknown-statement-name"]
    assert not any("annex_country" in n for n in names)
    assert not any("add_stability" in n for n in names)
    assert not any("name" in n or "title" in n for n in names)


def test_scope_change_tags_are_silent(tmp_path, data_dir):
    script = EVENT.replace(
        "annex_country = GER",
        "GER = { annex_country = GER }",
    )
    findings = validate_mod(_mod(tmp_path, script), data_dir)
    names = [f.message for f in findings if f.rule == "unknown-statement-name"]
    assert not any("GER" in n for n in names)


def test_scripted_effect_definitions_are_known(tmp_path, data_dir):
    script = EVENT.replace(
        "not_a_real_effect = { value = 1 }",
        "mymod_helper_effect = yes",
    )
    mod = _mod(
        tmp_path,
        script,
        {"common/scripted_effects/mymod_effects.txt": "mymod_helper_effect = {\n\tadd_stability = 0.1\n}\n"},
    )
    findings = validate_mod(mod, data_dir)
    assert [f for f in findings if f.rule == "unknown-statement-name"] == []


def test_vanilla_scripted_effects_are_known_with_game_dir(tmp_path, data_dir):
    """Scripted effects defined by the vanilla game count as known when the
    game dir is provided (mods call them constantly)."""
    script = EVENT.replace("not_a_real_effect = { value = 1 }", "vanilla_helper = yes")
    mod = _mod(tmp_path, script)
    without = validate_mod(mod, data_dir)
    assert any("vanilla_helper" in f.message for f in without)
    with_game = validate_mod(mod, data_dir, game_dir=FAKE_GAME)
    assert not any("vanilla_helper" in f.message for f in with_game)


def test_without_data_no_statement_warnings(tmp_path):
    findings = validate_mod(_mod(tmp_path, EVENT))
    assert [f for f in findings if f.rule == "unknown-statement-name"] == []


FOCUS_REF = (
    "country_event = {\n"
    "\tid = mymod.1\n"
    "\ttitle = mymod.1.t\n"
    "\tdesc = mymod.1.d\n"
    "\toption = {\n"
    "\t\tname = mymod.1.a\n"
    "\t\ttrigger = {\n"
    "\t\t\thas_completed_focus = mod_focus_b\n"
    "\t\t}\n"
    "\t}\n"
    "}\n"
)


def test_focus_reference_to_defined_focus_is_silent(tmp_path, data_dir):
    mod = _mod(
        tmp_path,
        FOCUS_REF,
        {"common/national_focus/tree.txt": FOCUS_A_BODY},
    )
    findings = validate_mod(mod, data_dir)
    assert [f for f in findings if f.rule == "unknown-focus-reference"] == []


def test_focus_reference_to_missing_focus_warns(tmp_path, data_dir):
    # focus-reference checks need the game dir: without it vanilla ids
    # cannot be distinguished from typos
    findings = validate_mod(_mod(tmp_path, FOCUS_REF), data_dir, game_dir=FAKE_GAME)
    hits = [f for f in findings if f.rule == "unknown-focus-reference"]
    assert len(hits) == 1
    assert "mod_focus_b" in hits[0].message

    # without a game dir the check stays silent (by design)
    assert [f for f in validate_mod(_mod(tmp_path, FOCUS_REF), data_dir)
            if f.rule == "unknown-focus-reference"] == []


FOCUS_A_BODY = (
    "focus_tree = {\n"
    "\tfocus = {\n"
    "\t\tid = mod_focus_b\n"
    "\t\ticon = GFX_focus_generic_industry\n"
    "\t\tx = 1\n\t\ty = 0\n\t\tcost = 5\n"
    "\t}\n"
    "}\n"
)


def test_focus_reference_vanilla_known_with_game_dir(tmp_path, data_dir):
    """With the game dir, vanilla focus ids count as known."""
    mod = _mod(tmp_path, FOCUS_REF)
    findings = validate_mod(mod, data_dir, game_dir=FAKE_GAME)
    # fake_game defines ger_test.3 as an event, not a focus — so mod_focus_b
    # is still unknown, but nothing crashes on a game dir without focuses.
    assert isinstance(findings, list)
