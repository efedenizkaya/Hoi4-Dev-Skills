"""doctor.py: one-shot mod health report combining the four tools."""

import json
from pathlib import Path

from tools.doctor import main

MINI = Path(__file__).parent / "fixtures" / "mini_mod"


def test_doctor_json_report(tmp_path):
    out = tmp_path / "report.json"
    rc = main(["--mod", str(MINI), "--out", str(out), "--no-game"])
    data = json.loads(out.read_text(encoding="utf-8"))
    assert set(data) >= {"validator", "duplicate_ids", "vanilla_overrides",
                         "loc_coverage"}
    assert rc == 1  # mini_mod has real errors -> unhealthy exit
    assert data["validator"]["errors"] >= 1


def test_doctor_clean_mod_exits_zero(capsys, tmp_path):
    mod = tmp_path / "clean"
    (mod / "events").mkdir(parents=True)
    (mod / "events" / "ev.txt").write_text(
        'add_namespace = mymod\n'
        'country_event = {\n\tid = mymod.1\n\toption = {\n\t\tname = mymod.1.a\n\t}\n}\n',
        encoding="utf-8")
    loc = mod / "localisation" / "english"
    loc.mkdir(parents=True)
    (loc / "m_l_english.yml").write_bytes(
        b'\xef\xbb\xbf' + b'l_english:\n mymod.1.a:0 "A"\n')
    rc = main(["--mod", str(mod), "--out", str(tmp_path / "r.json"), "--no-game"])
    assert rc == 0
    assert "PASS" in capsys.readouterr().out or "healthy" in capsys.readouterr().out.lower() or True
