"""Focus-tree rules v3: relative-position overlap exemption, duplicate
focus ids, vanilla-aware prerequisite targets (from the owner audit)."""

from pathlib import Path

from tools.validate import validate_mod

FOCUS = (
    "focus_tree = {{\n"
    "\tfocus = {{\n"
    "\t\tid = mod_{tag}\n"
    "\t\ticon = GFX_focus_generic_industry\n"
    "\t\tx = {x}\n"
    "\t\ty = {y}\n"
    "\t\tcost = 5\n"
    "{extra}"
    "\t}}\n"
    "}}\n"
)


def _write(tmp_path: Path, body: str) -> Path:
    (tmp_path / "common" / "national_focus").mkdir(parents=True)
    (tmp_path / "common" / "national_focus" / "tree.txt").write_text(body, encoding="utf-8")
    return tmp_path


def test_duplicate_focus_id_flagged(tmp_path):
    body = FOCUS.format(tag="one", x=1, y=0, extra="") + FOCUS.format(
        tag="one", x=2, y=0, extra=""
    ).replace("mod_one", "mod_one")
    # second block keeps the same id on purpose
    findings = validate_mod(_write(tmp_path, body))
    hits = [f for f in findings if f.rule == "duplicate-focus-id"]
    assert len(hits) == 1
    assert hits[0].severity == "error"


def test_relative_positioned_focuses_do_not_overlap(tmp_path):
    body = (
        FOCUS.format(tag="anchor", x=1, y=0, extra="").replace(
            "\t\tx = 1", "\t\tx = 1"
        )
        + FOCUS.format(tag="child", x=0, y=1, extra="").replace(
            "\t\tx = 0",
            "\t\trelative_position_id = mod_anchor\n\t\tx = 0",
        )
        + FOCUS.format(tag="other", x=0, y=1, extra="")
    )
    findings = validate_mod(_write(tmp_path, body))
    # mod_child is relative to mod_anchor (absolute 1,1); mod_other sits at
    # absolute 0,1 — no true collision, and relative focuses are exempt.
    hits = [f for f in findings if f.rule == "focus-position-overlap"]
    assert hits == []


def test_prerequisite_to_vanilla_focus_not_an_error(tmp_path, monkeypatch):
    import tools.validate as v

    mod = _write(
        tmp_path,
        FOCUS.format(tag="base", x=1, y=0, extra="").replace(
            "\t\tcost = 5",
            "\t\tcost = 5\n\t\tprerequisite = { focus = vanilla_focus_1 }",
        ),
    )
    # without game dir: still an error (we cannot know vanilla)
    findings = validate_mod(mod)
    assert any(f.rule == "missing-focus-prerequisite" for f in findings)
    # with the fake game dir (defines vanilla_focus_1): silent
    game = Path(__file__).parent / "fixtures" / "fake_game"
    findings = validate_mod(mod, game_dir=game)
    assert not any(f.rule == "missing-focus-prerequisite" for f in findings)
