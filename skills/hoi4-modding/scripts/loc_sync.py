"""Generate translation stubs for localisation keys missing in a language.

For every key defined in `localisation/english/` but missing from a target
language folder, writes the key with the ENGLISH text into ONE generated
file per language: `zz_sync_l_<lang>.yml` (additive — the zz_ prefix sorts
last; see mod-structure load order). Existing translations anywhere in the
language folder are respected and never overwritten. The user then edits
the stubs in place.

This is the only loc tool that WRITES, and it writes only the single
generated file — user files are never modified.

Usage:
    python tools/loc_sync.py --mod <mod_dir> --lang german[,french,...]
                             [--dry-run]

Exit codes: 0 = ok, 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_LOC_KEY_TEXT_RE = re.compile(r"^\s*([A-Za-z][\w.\-]*):\d*\s*\"(.*)\"\s*$", re.M)
_LOC_KEY_RE = re.compile(r"^\s*([A-Za-z][\w.\-]*):\d*\s*\"", re.M)


def _read_folder(folder: Path) -> tuple[dict[str, str], set[str]]:
    """english folder: key -> english text. Other folders: key -> None."""
    texts: dict[str, str] = {}
    keys: set[str] = set()
    if not folder.is_dir():
        return texts, keys
    for path in sorted(folder.glob("**/*.yml")):
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig", errors="replace")
        # BOM-less files are dead to the game: their keys do not count as
        # translated, but their text is still usable as a stub source
        for m in _LOC_KEY_TEXT_RE.finditer(text):
            key = m.group(1)
            if bom:
                keys.add(key)
                texts.setdefault(key, m.group(2))
            else:
                keys.add(key)
    return texts, keys


def sync_language(mod_dir: Path, lang: str) -> dict:
    loc = mod_dir / "localisation"
    en_texts, en_keys = _read_folder(loc / "english")
    _, have = _read_folder(loc / lang)
    missing = sorted(en_keys - have)

    target = loc / lang / f"zz_sync_l_{lang}.yml"
    existing_stub_text = target.read_text(encoding="utf-8-sig",
                                          errors="replace") if target.is_file() else ""
    existing_stub_keys = set(_LOC_KEY_RE.findall(existing_stub_text))

    to_add = [k for k in missing if k not in existing_stub_keys]
    return {
        "lang": lang,
        "english_keys": len(en_keys),
        "missing": missing,
        "to_add": to_add,
        "target": target,
        "en_texts": en_texts,
        "existing_stub_text": existing_stub_text,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate translation stubs")
    parser.add_argument("--mod", type=Path, required=True)
    parser.add_argument("--lang", required=True,
                        help="comma-separated language folders to sync")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    loc = args.mod / "localisation"
    if not (loc / "english").is_dir():
        print("error: no localisation/english baseline", file=sys.stderr)
        return 2

    langs = [l.strip() for l in args.lang.split(",") if l.strip()]
    total_added = 0
    for lang in langs:
        if not (loc / lang).is_dir():
            print(f"error: language folder localisation/{lang} does not exist",
                  file=sys.stderr)
            return 2
        plan = sync_language(args.mod, lang)
        to_add = plan["to_add"]
        print(f"{lang}: {len(plan['missing'])} missing, {len(to_add)} to add "
              f"-> {plan['target'].name}")
        if args.dry_run or not to_add:
            continue
        header = f"l_{lang}:\n"
        body = "".join(
            f' {k}:0 "{plan["en_texts"].get(k, "")}"\n' for k in to_add
        )
        if plan["existing_stub_text"]:
            # append to our own generated file only
            target = plan["target"]
            target.write_bytes(
                plan["target"].read_bytes().rstrip() + b"\n"
                + body.encode("utf-8"))
        else:
            plan["target"].write_bytes(
                b"\xef\xbb\xbf" + header.encode("utf-8") + body.encode("utf-8"))
        total_added += len(to_add)

    print(f"\n{total_added} stub(s) written — translate them in place; "
          "re-running never overwrites your translations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
