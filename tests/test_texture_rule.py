"""Asset Workshop validation: texturefile referenced by a mod .gfx must
exist on disk (mod gfx/, or game gfx/ when game_dir is given)."""

from pathlib import Path

from tools.validate import validate_mod

FAKE_GAME = Path(__file__).parent / "fixtures" / "fake_game"
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")


def _gfx(mod_dir: Path, sprite: str, texture: str) -> None:
    interface = mod_dir / "interface"
    interface.mkdir(parents=True, exist_ok=True)
    with (interface / "mymod.gfx").open("a", encoding="utf-8") as f:
        f.write(f'spriteTypes = {{\n\tSpriteType = {{\n\t\tname = "{sprite}"\n'
                f'\t\ttexturefile = "{texture}"\n\t}}\n}}\n')


def test_missing_texture_file_flagged(tmp_path):
    _gfx(tmp_path, "GFX_mymod_icon", "gfx/mymod/icon.dds")
    findings = validate_mod(tmp_path, game_dir=FAKE_GAME)
    hits = [f for f in findings if f.rule == "missing-texture-file"]
    assert len(hits) == 1
    assert hits[0].severity == "warning"
    assert "gfx/mymod/icon.dds" in hits[0].message


def test_existing_texture_silent(tmp_path):
    _gfx(tmp_path, "GFX_mymod_icon", "gfx/mymod/icon.dds")
    tex = tmp_path / "gfx" / "mymod" / "icon.dds"
    tex.parent.mkdir(parents=True, exist_ok=True)
    tex.write_bytes(b"DDS ")
    findings = validate_mod(tmp_path, game_dir=FAKE_GAME)
    assert not [f for f in findings if f.rule == "missing-texture-file"]


def test_game_owned_texture_silent_with_real_game_dir(tmp_path):
    """A mod .gfx can reference vanilla texture paths — with the game dir
    given they resolve against the game's gfx tree."""
    _gfx(tmp_path, "GFX_mymod_vanilla_ref",
         "gfx/interface/goals/focus_generic_industry.dds")
    findings = validate_mod(tmp_path, game_dir=FAKE_GAME)
    assert [f for f in findings if f.rule == "missing-texture-file"] == []
