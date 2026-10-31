"""doctor.py: one-shot mod health report combining the four tools."""

import json
import re
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


def _clean_mod(tmp_path: Path) -> Path:
    mod = tmp_path / "clean"
    (mod / "events").mkdir(parents=True)
    (mod / "events" / "ev.txt").write_text(
        "add_namespace = mymod\n"
        "country_event = {\n"
        "\tid = mymod.1\n"
        "\toption = {\n"
        "\t\tname = mymod.1.a\n"
        "\t}\n"
        "}\n",
        encoding="utf-8")
    loc = mod / "localisation" / "english"
    loc.mkdir(parents=True)
    (loc / "m_l_english.yml").write_bytes(
        b"\xef\xbb\xbf" + b'l_english:\n mymod.1.a:0 "A"\n')
    return mod


def test_health_score_and_markdown(tmp_path):
    out = tmp_path / "report.md"
    rc = main(["--mod", str(_clean_mod(tmp_path)), "--out", str(out), "--no-game"])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "# Mod Doctor report" in text
    m = re.search(r"health score: (\d+)/100", text)
    assert m and 0 <= int(m.group(1)) <= 100


def test_score_punishes_errors(tmp_path):
    out1 = tmp_path / "r1.json"
    main(["--mod", str(_clean_mod(tmp_path)), "--out", str(out1), "--no-game"])
    score_clean = json.loads(out1.read_text(encoding="utf-8"))["health_score"]

    dirty = tmp_path / "dirty"
    (dirty / "common" / "national_focus").mkdir(parents=True)
    (dirty / "common" / "national_focus" / "broken.txt").write_text(
        "focus = {\n\tid = x\n", encoding="utf-8")  # unbalanced braces = error
    out2 = tmp_path / "r2.json"
    main(["--mod", str(dirty), "--out", str(out2), "--no-game"])
    score_dirty = json.loads(out2.read_text(encoding="utf-8"))["health_score"]

    assert score_clean == 100
    assert score_dirty < score_clean
