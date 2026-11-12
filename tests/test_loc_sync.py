"""loc_sync: generate translation STUBS for keys missing in a language
folder. Only ever writes/updates ONE generated file per language
(`zz_sync_l_<lang>.yml`) — user files are never touched. Existing
translations anywhere in the language folder are respected."""

import json
from pathlib import Path

from tools.loc_sync import main


def _mod(tmp_path: Path) -> Path:
    loc = tmp_path / "localisation"
    en = loc / "english"
    en.mkdir(parents=True)
    (en / "a_l_english.yml").write_bytes(
        b"\xef\xbb\xbf"
        + b'l_english:\n'
        + b' shared.one:0 "One"\n'
        + b' shared.two:0 "Two"\n'
        + b' shared.three:0 "Three"\n')
    de = loc / "german"
    de.mkdir(parents=True)
    (de / "user_l_german.yml").write_bytes(
        b"\xef\xbb\xbf"
        + b'l_german:\n'
        + b' shared.one:0 "Eins"\n')   # user translation: must be preserved
    return tmp_path


def test_generates_stub_with_missing_keys_only(tmp_path):
    mod = _mod(tmp_path)
    rc = main(["--mod", str(mod), "--lang", "german"])
    assert rc == 0
    gen = mod / "localisation" / "german" / "zz_sync_l_german.yml"
    raw = gen.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")                       # BOM
    text = raw.decode("utf-8-sig")
    assert "l_german:" in text
    assert 'shared.two:0 "Two"' in text                          # english stub
    assert 'shared.three:0 "Three"' in text
    assert "shared.one" not in text                              # already translated
    # user file untouched
    user_text = (mod / "localisation/german/user_l_german.yml").read_text(
        encoding="utf-8-sig")
    assert "shared.two" not in user_text
    assert 'shared.one:0 "Eins"' in user_text


def test_idempotent_rerun(tmp_path):
    mod = _mod(tmp_path)
    main(["--mod", str(mod), "--lang", "german"])
    before = (mod / "localisation/german/zz_sync_l_german.yml").read_bytes()
    main(["--mod", str(mod), "--lang", "german"])
    after = (mod / "localisation/german/zz_sync_l_german.yml").read_bytes()
    assert before == after


def test_dry_run_writes_nothing(tmp_path):
    mod = _mod(tmp_path)
    rc = main(["--mod", str(mod), "--lang", "german", "--dry-run"])
    out_gen = mod / "localisation" / "german" / "zz_sync_l_german.yml"
    assert rc == 0
    assert not out_gen.exists()


def test_respects_translation_in_second_file(tmp_path):
    mod = _mod(tmp_path)
    # user translates shared.two in ANOTHER file in the same language
    extra = mod / "localisation" / "german" / "extra_l_german.yml"
    extra.write_bytes(b"\xef\xbb\xbf" + b'l_german:\n shared.two:0 "Zwei"\n')
    main(["--mod", str(mod), "--lang", "german"])
    gen = (mod / "localisation/german/zz_sync_l_german.yml").read_text(
        encoding="utf-8-sig")
    assert "shared.two" not in gen           # translated elsewhere -> skip
    assert "shared.three" in gen             # still missing -> synced
