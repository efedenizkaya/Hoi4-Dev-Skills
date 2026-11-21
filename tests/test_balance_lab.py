"""Balance Lab: static per-country strength extraction from history files
(states: buildings/manpower/ownership; country files: starting ideas).
Static 1936-build snapshot — does NOT simulate gameplay."""

import json
from pathlib import Path

from tools.balance_lab import main


def _write(tmp_path: Path, rel: str, content: str) -> None:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


STATE_GER = """state={
\tid=10
\tname="STATE_10"
\tmanpower = 3000000
\tstate_category = large_city
\thistory={
\t\towner = GER
\t\tbuildings = {
\t\t\tindustrial_complex = 8
\t\t\tarms_factory = 5
\t\t\tdockyard = 0
\t\t\tinfrastructure = 4
\t\t}
\t}
\tprovinces={ 1 2 3 }
}
"""

STATE_POL = """state={
\tid=20
\tname="STATE_20"
\tmanpower = 1500000
\tstate_category = rural
\thistory={
\t\towner = POL
\t\tbuildings = {
\t\t\tindustrial_complex = 4
\t\t\tarms_factory = 2
\t\t}
\t}
\tprovinces={ 10 11 }
}
"""


def _make_mod(tmp_path: Path) -> Path:
    _write(tmp_path, "history/states/10-Germany.txt", STATE_GER)
    _write(tmp_path, "history/states/20-Poland.txt", STATE_POL)
    _write(tmp_path, "history/countries/GER - Germany.txt",
           "capital = 10\nadd_ideas = GER_start_spirit\n")
    _write(tmp_path, "history/countries/POL - Poland.txt",
           "capital = 20\n")
    return tmp_path


def test_per_country_strength_totals(tmp_path):
    mod = _make_mod(tmp_path)
    from tools.balance_lab import build_report

    report = build_report(mod)
    tags = {c["tag"]: c for c in report["countries"]}
    assert tags["GER"]["civilian_factories"] == 8
    assert tags["GER"]["military_factories"] == 5
    assert tags["GER"]["dockyards"] == 0
    assert tags["GER"]["manpower"] == 3000000
    assert tags["GER"]["states"] == 1
    assert tags["POL"]["civilian_factories"] == 4
    assert tags["POL"]["starting_ideas"] == []


def test_starting_ideas_extracted(tmp_path):
    mod = _make_mod(tmp_path)
    _write(mod, "history/countries/GER - Germany.txt",
           "capital = 10\nadd_ideas = GER_start_spirit\n")
    from tools.balance_lab import build_report

    report = build_report(mod)
    tags = {c["tag"]: c for c in report["countries"]}
    assert tags["GER"]["starting_ideas"] == ["GER_start_spirit"]


def test_comparative_markdown(tmp_path):
    mod = _make_mod(tmp_path)
    out = tmp_path / "balance.md"
    rc = main(["--mod", str(mod), "--out", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "civ factories" in text.lower()
    assert "GER" in text and "POL" in text
    # static-snapshot honesty note
    assert "does not simulate" in text.lower()


def test_json_output(tmp_path):
    mod = _make_mod(tmp_path)
    main(["--mod", str(mod), "--json", "--out", str(tmp_path / "r.json")])
    data = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    assert {c["tag"] for c in data["countries"]} == {"GER", "POL"}
