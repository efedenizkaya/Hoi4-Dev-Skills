"""Focus-tree regressions RESTORED (audit: the v0.18.0 rewrite of
test_validate_focus.py dropped three pins). Each test here protects a
behavior that once regressed or has no other coverage."""

from pathlib import Path

from tools.validate import validate_mod

FAKE_GAME = Path(__file__).parent / "fixtures" / "fake_game"


def _tree(tmp_path: Path, body: str) -> Path:
    (tmp_path / "common" / "national_focus").mkdir(parents=True)
    (tmp_path / "common" / "national_focus" / "tree.txt").write_text(body, encoding="utf-8")
    return tmp_path


def _focus(fid: str, x: int, y: int, extra: str = "") -> str:
    return (
        f"\tfocus = {{\n"
        f"\t\tid = {fid}\n"
        f"\t\ticon = GFX_focus_generic_industry\n"
        f"\t\tx = {x}\n"
        f"\t\ty = {y}\n"
        f"\t\tcost = 5\n"
        f"{extra}"
        f"\t}}\n"
    )


def test_duplicate_focus_id(tmp_path):
    body = "focus_tree = {\n" + _focus("mod_a", 1, 0) + _focus("mod_a", 2, 0) + "}\n"
    findings = validate_mod(_tree(tmp_path, body))
    hits = [f for f in findings if f.rule == "duplicate-focus-id"]
    assert len(hits) == 1
    assert hits[0].severity == "error"


def test_relative_positioned_focuses_do_not_overlap(tmp_path):
    """A focus positioned relative to another focus shares no absolute grid
    cell with a same-offset sibling under a different anchor (regression
    pin — no other test carries the `relative_position_id` exemption)."""
    body = (
        "focus_tree = {\n"
        + _focus("mod_anchor", 1, 0)
        + _focus("mod_child", 0, 1, "\t\trelative_position_id = mod_anchor\n")
        + _focus("mod_other", 0, 1)
        + "}\n"
    )
    findings = validate_mod(_tree(tmp_path, body))
    # mod_child is at absolute (1,1); mod_other at (0,1) -> no collision
    assert [f for f in findings if f.rule == "focus-position-overlap"] == []


def test_prerequisite_to_vanilla_focus(tmp_path):
    """A prerequisite targeting a vanilla focus is legitimate when the game
    dir is provided; without it, it stays an error."""
    mod = _tree(
        tmp_path,
        "focus_tree = {\n"
        + _focus("mod_base", 1, 0, "\t\tprerequisite = { focus = vanilla_focus_1 }\n")
        + "}\n",
    )
    without = validate_mod(mod)
    assert any(f.rule == "missing-focus-prerequisite" for f in without)
    with_game = validate_mod(mod, game_dir=FAKE_GAME)
    assert not any(f.rule == "missing-focus-prerequisite" for f in with_game)
