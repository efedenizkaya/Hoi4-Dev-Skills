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


def test_unknown_modifier_name_warned(tmp_path, data_dir):
    """Modifier keys inside idea/dynamic-modifier blocks are checked against
    the extracted modifiers database (templated names match)."""
    (tmp_path / "common" / "ideas").mkdir(parents=True)
    (tmp_path / "common" / "ideas" / "mod_ideas.txt").write_text(
        "mymod_spirit = {\n"
        "\tmodifier = {\n"
        "\t\tpolitical_power_gain = 0.5\n"   # real template name? verify below
        "\t\tnot_a_real_modifier_xyz = 1\n"
        "\t}\n"
        "}\n",
        encoding="utf-8",
    )
    findings = validate_mod(_mod(tmp_path, EVENT), data_dir)
    hits = [f for f in findings if f.rule == "unknown-modifier-name"]
    assert [h.message.split(":")[0] for h in hits] == ["not_a_real_modifier_xyz"]


def test_weight_modifier_blocks_stay_silent(tmp_path, data_dir):
    """ai_will_do / tree-country `modifier = { factor/add }` blocks are
    weight grammar, not modifier-name lists."""
    (tmp_path / "common" / "ideas").mkdir(parents=True)
    (tmp_path / "common" / "ideas" / "mod_ideas.txt").write_text(
        "mymod_spirit = {\n"
        "\tai_will_do = {\n"
        "\t\tmodifier = { factor = 2 totally_bogus_key = 1 }\n"
        "\t}\n"
        "}\n",
        encoding="utf-8",
    )
    findings = validate_mod(_mod(tmp_path, EVENT), data_dir)
    assert [f for f in findings if f.rule == "unknown-modifier-name"] == []


def test_unknown_sprite_warned_with_game_dir(tmp_path, data_dir):
    """icon/picture/background GFX references must exist in mod or vanilla
    interface/*.gfx (game_dir required — DLC sprites live there)."""
    (tmp_path / "common" / "national_focus").mkdir(parents=True)
    (tmp_path / "common" / "national_focus" / "tree.txt").write_text(
        "focus_tree = {\n"
        "\tfocus = {\n"
        "\t\tid = mod_f\n"
        "\t\ticon = GFX_focus_generic_industry\n"   # declared in fake_game gfx
        "\t\tx = 1\n\t\ty = 0\n\t\tcost = 5\n"
        "\t}\n"
        "\tfocus = {\n"
        "\t\tid = mod_g\n"
        "\t\ticon = GFX_focus_totally_made_up\n"
        "\t\tx = 2\n\t\ty = 0\n\t\tcost = 5\n"
        "\t}\n"
        "}\n",
        encoding="utf-8",
    )
    findings = validate_mod(_mod(tmp_path, EVENT), data_dir, game_dir=FAKE_GAME)
    hits = [f for f in findings if f.rule == "unknown-sprite"]
    assert [h.message.split(":")[0] for h in hits] == ["GFX_focus_totally_made_up"]


def test_unknown_on_action_warned_with_game_dir(tmp_path, data_dir):
    """Mod on_action hook names must exist in the vanilla hook list."""
    (tmp_path / "common" / "on_actions").mkdir(parents=True)
    (tmp_path / "common" / "on_actions" / "mod_hooks.txt").write_text(
        "on_actions = {\n"
        "\ton_startup = { effect = { mymod_init = yes } }\n"
        "\ton_totally_bogus_hook = { effect = { x = yes } }\n"
        "}\n",
        encoding="utf-8",
    )
    findings = validate_mod(_mod(tmp_path, EVENT), data_dir, game_dir=FAKE_GAME)
    hits = [f for f in findings if f.rule == "unknown-on-action"]
    assert [h.message.split(":")[0] for h in hits] == ["on_totally_bogus_hook"]


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
    ref = FOCUS_REF.replace("mod_focus_b", "vanilla_focus_1")
    mod = _mod(tmp_path, ref)
    findings = validate_mod(mod, data_dir, game_dir=FAKE_GAME)
    assert [f for f in findings if f.rule == "unknown-focus-reference"] == []
    # a garbage id is still caught
    bad = FOCUS_REF.replace("mod_focus_b", "definitely_not_a_focus")
    findings = validate_mod(_mod(tmp_path, bad), data_dir, game_dir=FAKE_GAME)
    assert any("definitely_not_a_focus" in f.message
               for f in findings if f.rule == "unknown-focus-reference")
