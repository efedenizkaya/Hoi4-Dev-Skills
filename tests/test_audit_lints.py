"""Audit-lint tests (roadmap item 8): descriptor replace_path, undefined
event/idea references, unused event-pattern loc keys, periodic hooks."""

from pathlib import Path

from tools.validate import validate_mod

FAKE_GAME = Path(__file__).parent / "fixtures" / "fake_game"

EVENT = (
    "add_namespace = mymod\n"
    "country_event = {\n"
    "\tid = mymod.1\n"
    "\toption = {\n"
    "\t\tname = mymod.1.a\n"
    "\t\tcountry_event = { id = mymod.2 }\n"      # defined below
    "\t\tcountry_event = { id = ghost.9 }\n"       # defined nowhere
    "\t}\n"
    "}\n"
    "country_event = {\n"
    "\tid = mymod.2\n"
    "\toption = {\n"
    "\t\tname = mymod.2.a\n"
    "\t\tadd_ideas = mymod_idea\n"                 # defined below
    "\t\tadd_ideas = ghost_idea\n"                 # defined nowhere (game-aware)
    "\t}\n"
    "}\n"
)


def _mod(tmp_path: Path, extra: dict[str, str] | None = None) -> Path:
    (tmp_path / "events").mkdir(parents=True)
    (tmp_path / "events" / "ev.txt").write_text(EVENT, encoding="utf-8")
    (tmp_path / "common" / "ideas").mkdir(parents=True)
    (tmp_path / "common" / "ideas" / "ideas.txt").write_text(
        "mymod_category = {\n\tmymod_idea = {\n\t\tmodifier = {}\n\t}\n}\n",
        encoding="utf-8")
    for rel, content in (extra or {}).items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return tmp_path


def test_undefined_event_reference_flagged_with_game_dir(tmp_path):
    findings = validate_mod(_mod(tmp_path), game_dir=FAKE_GAME)
    hits = [f for f in findings if f.rule == "unknown-event-reference"]
    ids = {f.message.split(":")[0] for f in hits}
    assert ids == {"ghost.9"}            # mymod.2 is defined -> silent


def test_undefined_idea_reference_flagged_with_game_dir(tmp_path):
    findings = validate_mod(_mod(tmp_path), game_dir=FAKE_GAME)
    hits = [f for f in findings if f.rule == "unknown-idea-reference"]
    ids = {f.message.split(":")[0] for f in hits}
    assert ids == {"ghost_idea"}         # mymod_idea defined in mod


def test_unused_event_pattern_loc_key(tmp_path):
    mod = _mod(tmp_path)
    loc = mod / "localisation" / "english"
    loc.mkdir(parents=True)
    (loc / "m_l_english.yml").write_bytes(
        b"\xef\xbb\xbf"
        + b'l_english:\n'
        + b' mymod.1.a:0 "A"\n'          # used by the event
        + b' mymod.99.z:0 "Leftover"\n'  # event-pattern key, referenced nowhere
        + b' dynamic_menu_title:0 "Not event-pattern"\n')  # out of scope
    findings = validate_mod(mod)
    hits = [f for f in findings if f.rule == "unused-loc-key"]
    assert [f.message.split(":")[0] for f in hits] == ["mymod.99.z"]


def test_replace_path_flagged(tmp_path):
    (tmp_path / "descriptor.mod").write_text(
        'name="X"\nreplace_path="common/land_doctrines"\n', encoding="utf-8")
    findings = validate_mod(tmp_path)
    hits = [f for f in findings if f.rule == "replace-path-used"]
    assert len(hits) == 1
    assert hits[0].severity == "warning"


def test_periodic_on_action_hook_warns_heuristic(tmp_path, data_dir=None):
    (tmp_path / "common" / "on_actions").mkdir(parents=True)
    (tmp_path / "common" / "on_actions" / "hooks.txt").write_text(
        "on_actions = {\n"
        "\ton_daily = { effect = { mymod_tick = yes } }\n"
        "\ton_startup = { effect = { mymod_init = yes } }\n"
        "}\n",
        encoding="utf-8",
    )
    findings = validate_mod(tmp_path)
    hits = [f for f in findings if f.rule == "periodic-effect-performance"]
    assert len(hits) == 1
    assert hits[0].message.startswith("(heuristic)")
