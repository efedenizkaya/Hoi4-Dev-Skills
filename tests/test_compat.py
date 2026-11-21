"""Compatibility Lab: cross-mod conflict detection (id collisions, shared
vanilla shadows, loc key collisions). Analysis only — never modifies mods."""

import json
from pathlib import Path

from tools.compat import main

MOD_A = Path(__file__).parent / "fixtures" / "compat_a"
MOD_B = Path(__file__).parent / "fixtures" / "compat_b"


def test_json_report_collisions(capsys):
    rc = main(["--mod", str(MOD_A), "--mod", str(MOD_B), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert rc == 1  # conflicts present
    ids = {(c["kind"], c["id"]) for c in data["id_collisions"]}
    assert ("event", "shared.1") in ids
    # both mods define shared.1 — files from BOTH mods listed
    ev = next(c for c in data["id_collisions"] if c["id"] == "shared.1")
    assert len(ev["definitions"]) == 2
    assert any("compat_a" in d for d in ev["definitions"])
    assert any("compat_b" in d for d in ev["definitions"])


def test_shared_vanilla_shadow_reported(capsys):
    """Hermetic: uses the fake game fixture, not the local install."""
    game = Path(__file__).parent / "fixtures" / "fake_game"
    main(["--mod", str(MOD_A), "--mod", str(MOD_B), "--game-dir",
          str(game), "--json"])
    data = json.loads(capsys.readouterr().out)
    shadows = {s["file"]: s["mods"] for s in data["vanilla_shadows"]}
    assert "common/ideas/_economic.txt" in shadows
    assert {Path(m).name for m in shadows["common/ideas/_economic.txt"]} == {"compat_a", "compat_b"}


def test_loc_key_collision(capsys):
    main(["--mod", str(MOD_A), "--mod", str(MOD_B), "--json"])
    data = json.loads(capsys.readouterr().out)
    loc = {c["key"]: c["mods"] for c in data["loc_collisions"]}
    assert "shared.title" in loc
    assert {Path(m).name for m in loc["shared.title"]} == {"compat_a", "compat_b"}


def test_clean_pair_exits_zero(capsys, tmp_path):
    for name in ("mod1", "mod2"):
        ev = tmp_path / name / "events"
        ev.mkdir(parents=True)
        (ev / "ev.txt").write_text(
            f'add_namespace = {name}\ncountry_event = {{\n\tid = {name}.1\n}}\n',
            encoding="utf-8")
    rc = main(["--mod", str(tmp_path / "mod1"), "--mod", str(tmp_path / "mod2"),
               "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["id_collisions"] == []
    assert data["vanilla_shadows"] == []
    assert data["loc_collisions"] == []
    assert rc == 0


def test_single_mod_exits_two(capsys):
    rc = main(["--mod", str(MOD_A)])
    assert rc == 2
