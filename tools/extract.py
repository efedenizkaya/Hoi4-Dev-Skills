"""Extract version-stamped HOI4 scripting data from a local game install.

Reads the official ``documentation/*.md`` files the game ships and
regenerates each patch, plus the game version from ``launcher-settings.json``,
and writes JSON databases + a sanitized summary. Nothing game-derived is
committed to the hoi4-dev-skills repository — run this against your own
install.

Usage:
    python tools/extract.py                     # auto-detect the game
    python tools/extract.py --game-dir <path>   # explicit install
    python tools/extract.py --out <dir>         # output root (default: extracted/)
    python tools/extract.py --summary-out <f>   # where to write summary.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

try:  # imported as a package module
    from .pdx_doc_parser import GAME_DOC_FILES, parse_effects_or_triggers, parse_modifiers
except ImportError:  # run as a script: python tools/extract.py
    from pdx_doc_parser import GAME_DOC_FILES, parse_effects_or_triggers, parse_modifiers

DEFAULT_STEAM_PATH = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV"
)


def find_game_dir() -> Path | None:
    """Locate a HOI4 install: env var first, then the default Steam path."""
    env = os.environ.get("HOI4_GAME_DIR", "").strip()
    if env:
        candidate = Path(env)
        if candidate.is_dir():
            return candidate
    if DEFAULT_STEAM_PATH.is_dir():
        return DEFAULT_STEAM_PATH
    return None


def _read_version(game_dir: Path) -> str:
    settings = game_dir / "launcher-settings.json"
    data = json.loads(settings.read_text(encoding="utf-8-sig"))
    version = data.get("rawVersion")
    if not version:
        raise KeyError(f"rawVersion missing from {settings}")
    return str(version)


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def extract(game_dir: Path, out_dir: Path, summary_out: Path | None = None) -> Path:
    """Extract all supported documentation files into ``<out_dir>/<version>/``.

    Returns the written data directory. Raises FileNotFoundError when the
    game dir has no ``documentation`` folder.
    """
    doc_dir = game_dir / "documentation"
    if not doc_dir.is_dir():
        raise FileNotFoundError(f"no documentation folder in {game_dir}")

    version = _read_version(game_dir)
    data_dir = out_dir / version
    counts: dict[str, object] = {}

    for stem, kind in GAME_DOC_FILES.items():
        entries = parse_effects_or_triggers(doc_dir / f"{stem}.md", kind)
        _write_json(data_dir / f"{kind}s.json", [asdict(e) for e in entries])
        counts[f"{kind}s"] = len(entries)

    modifiers = parse_modifiers(doc_dir / "modifiers_documentation.md")
    _write_json(data_dir / "modifiers.json", modifiers)
    counts["modifiers"] = {k: len(v) for k, v in sorted(modifiers.items())}

    summary = {
        "gameVersion": version,
        "counts": counts,
        "extractedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if summary_out is not None:
        _write_json(summary_out, summary)
    else:
        _write_json(data_dir / "summary.json", summary)
    return data_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game-dir", type=Path, help="HOI4 install root")
    parser.add_argument("--out", type=Path, default=Path("extracted"))
    parser.add_argument("--summary-out", type=Path, default=None)
    args = parser.parse_args(argv)

    game_dir = args.game_dir or find_game_dir()
    if game_dir is None:
        print(
            "error: could not find the HOI4 install. Set --game-dir or the "
            "HOI4_GAME_DIR environment variable.",
            file=sys.stderr,
        )
        return 2
    if not (game_dir / "launcher-settings.json").is_file():
        print(f"error: {game_dir} does not look like a HOI4 install", file=sys.stderr)
        return 2

    data_dir = extract(game_dir, args.out, args.summary_out)
    summary = json.loads((data_dir / "summary.json").read_text(encoding="utf-8"))
    print(f"game version : {summary['gameVersion']}")
    print(f"effects      : {summary['counts']['effects']}")
    print(f"triggers     : {summary['counts']['triggers']}")
    mod_scopes = summary["counts"]["modifiers"]
    print(
        f"modifiers    : {sum(mod_scopes.values())} across {len(mod_scopes)} scopes"
    )
    print(f"written to   : {data_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
