"""Scaffold tool: generates a playable, validator-clean mod skeleton."""

import json
from pathlib import Path

from tools.new_mod import main


def test_scaffold_generates_complete_skeleton(tmp_path):
    rc = main(["My Cool Mod", "--dir", str(tmp_path), "--version", "0.1.0"])
    assert rc == 0
    mod = tmp_path / "my_cool_mod"
    # descriptors
    descriptor = (tmp_path / "my_cool_mod.mod").read_text(encoding="utf-8")
    assert 'name="My Cool Mod"' in descriptor
    assert 'path="mod/my_cool_mod"' in descriptor
    inner = (mod / "descriptor.mod").read_text(encoding="utf-8")
    assert "path=" not in inner
    # folder tree
    for d in ["events", "common/national_focus", "common/decisions/categories",
              "localisation/english", "history/countries"]:
        assert (mod / d).is_dir(), d
    # loc file has BOM and the header
    raw = (mod / "localisation/english/my_cool_mod_l_english.yml").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert b"l_english:" in raw
    # event file declares its namespace
    events = (mod / "events/my_cool_mod_events.txt").read_text(encoding="utf-8")
    assert "add_namespace = my_cool_mod" in events
    assert "id = my_cool_mod.1" in events


def test_scaffold_output_passes_validator(tmp_path):
    from tools.validate import validate_mod

    main(["Test Mod", "--dir", str(tmp_path)])
    findings = validate_mod(tmp_path / "test_mod")
    assert findings == [], [str(f) for f in findings]


def test_scaffold_refuses_to_overwrite(tmp_path):
    main(["Clash", "--dir", str(tmp_path)])
    rc = main(["Clash", "--dir", str(tmp_path)])
    assert rc == 2
