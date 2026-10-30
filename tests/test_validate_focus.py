"""Focus-tree rules v2: prerequisite targets exist, mutual exclusivity is
bidirectional, x/y grid positions don't collide. All three rules are
grounded in the claims register (focus-fields, mutual-exclusive-both)."""

from pathlib import Path

from tools.validate import validate_mod

FIXTURES = Path(__file__).parent / "fixtures"


def _focus_mod(tmp_path: Path, body: str) -> Path:
    (tmp_path / "common" / "national_focus").mkdir(parents=True)
    (tmp_path / "common" / "national_focus" / "tree.txt").write_text(body, encoding="utf-8")
    return tmp_path


FOCUS_A = (
    "focus_tree = {\n"
    "\tfocus = {\n"
    "\t\tid = mod_focus_a\n"
    "\t\ticon = GFX_focus_generic_industry\n"
    "\t\tx = 1\n"
    "\t\ty = 0\n"
    "\t\tcost = 5\n"
    "\t\tprerequisite = { focus = mod_focus_b }\n"   # b is defined below
    "\t}\n"
    "\tfocus = {\n"
    "\t\tid = mod_focus_b\n"
    "\t\ticon = GFX_focus_generic_industry\n"
    "\t\tx = 1\n"
    "\t\ty = 1\n"
    "\t\tcost = 5\n"
    "\t}\n"
    "}\n"
)


def test_valid_prerequisites_pass(tmp_path):
    findings = validate_mod(_focus_mod(tmp_path, FOCUS_A))
    assert [f for f in findings if "focus" in f.rule] == []


def test_missing_prerequisite_target(tmp_path):
    body = FOCUS_A.replace("focus = mod_focus_b", "focus = mod_focus_nope")
    findings = validate_mod(_focus_mod(tmp_path, body))
    hits = [f for f in findings if f.rule == "missing-focus-prerequisite"]
    assert len(hits) == 1
    assert hits[0].severity == "error"
    assert "mod_focus_nope" in hits[0].message


def test_focus_finding_reports_focus_line(tmp_path):
    """The finding must point at the focus's real line in the FILE, not a
    block-relative offset (regression: lines were computed from the block
    start, always ~1)."""
    filler = "\n".join(["# filler"] * 40) + "\n"
    body = (
        filler
        + "focus_tree = {\n"
        + FOCUS_A.replace("focus = mod_focus_b", "focus = mod_focus_nope")
    )
    findings = validate_mod(_focus_mod(tmp_path, body))
    hits = [f for f in findings if f.rule == "missing-focus-prerequisite"]
    assert len(hits) == 1
    assert hits[0].line > 40, hits[0].line


def test_mutual_exclusivity_bidirectional_ok(tmp_path):
    body = (
        "focus_tree = {\n"
        "\tfocus = {\n"
        "\t\tid = mod_left\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 1\n\t\ty = 0\n\t\tcost = 5\n"
        "\t\tmutually_exclusive = { focus = mod_right }\n"
        "\t}\n"
        "\tfocus = {\n"
        "\t\tid = mod_right\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 3\n\t\ty = 0\n\t\tcost = 5\n"
        "\t\tmutually_exclusive = { focus = mod_left }\n"
        "\t}\n"
        "}\n"
    )
    findings = validate_mod(_focus_mod(tmp_path, body))
    assert [f for f in findings if f.rule == "unidirectional-mutual-exclusive"] == []


def test_unidirectional_mutual_exclusive_warns(tmp_path):
    body = (
        "focus_tree = {\n"
        "\tfocus = {\n"
        "\t\tid = mod_left\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 1\n\t\ty = 0\n\t\tcost = 5\n"
        "\t\tmutually_exclusive = { focus = mod_right }\n"
        "\t}\n"
        "\tfocus = {\n"
        "\t\tid = mod_right\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 3\n\t\ty = 0\n\t\tcost = 5\n"
        "\t}\n"
        "}\n"
    )
    findings = validate_mod(_focus_mod(tmp_path, body))
    hits = [f for f in findings if f.rule == "unidirectional-mutual-exclusive"]
    assert len(hits) == 1
    assert hits[0].severity == "warning"
    assert "mod_right" in hits[0].message


def test_focus_position_overlap_warns(tmp_path):
    body = (
        "focus_tree = {\n"
        "\tfocus = {\n"
        "\t\tid = mod_one\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 2\n\t\ty = 0\n\t\tcost = 5\n"
        "\t}\n"
        "\tfocus = {\n"
        "\t\tid = mod_two\n"
        "\t\ticon = GFX_focus_generic_industry\n"
        "\t\tx = 2\n\t\ty = 0\n\t\tcost = 5\n"
        "\t}\n"
        "}\n"
    )
    findings = validate_mod(_focus_mod(tmp_path, body))
    hits = [f for f in findings if f.rule == "focus-position-overlap"]
    assert len(hits) == 1
    assert hits[0].severity == "warning"
