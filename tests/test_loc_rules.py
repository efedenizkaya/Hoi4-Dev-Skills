"""loc-language-mismatch subfolder semantics (audit fix): the language is
the FIRST folder under localisation/, subfolders under it are common, and
files sitting directly in localisation/ are exempt."""

from pathlib import Path

from tools.validate import validate_mod


def _mod_with_loc(tmp_path: Path, rel: str, header: str) -> Path:
    loc = tmp_path / "localisation"
    f = loc / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(b"\xef\xbb\xbf" + f"{header}:\n some.key:0 \"x\"\n".encode("utf-8"))
    return tmp_path


def test_subfolder_under_language_folder_is_clean(tmp_path):
    """localisation/english/events/x.yml is a NORMAL layout — the language
    is english (first folder), not events."""
    mod = _make = _mod_with_loc(tmp_path, "english/events/a_l_english.yml", "l_english")
    findings = validate_mod(mod)
    assert [f for f in findings if f.rule == "loc-language-mismatch"] == []


def test_real_mismatch_in_subfolder_flagged(tmp_path):
    mod = _mod_with_loc(tmp_path, "german/events/a_l_english.yml", "l_english")
    findings = validate_mod(mod)
    hits = [f for f in findings if f.rule == "loc-language-mismatch"]
    assert len(hits) == 1
    assert "german" in hits[0].message


def test_root_level_file_exempt(tmp_path):
    """Files sitting directly in localisation/ have no language folder —
    exempt rather than flagged as 'localisation' mismatch."""
    mod = _mod_with_loc(tmp_path, "b_l_english.yml", "l_english")
    findings = validate_mod(mod)
    assert [f for f in findings if f.rule == "loc-language-mismatch"] == []
