"""Check whether the skill's verified game version matches the installed one.

The skill stamps the game version it was verified against
(`game-version-verified` in SKILL.md frontmatter). When the player's
install moves to a newer patch, reference data goes stale — this tool
detects that and points at the migration workflow.

Usage:
    python tools/stale_check.py [--game-dir <dir>]

Exit codes: 0 = match, 1 = mismatch (suggests version_diff), 2 = usage error.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from .extract import find_game_dir
except ImportError:
    from extract import find_game_dir

# bundled layout: scripts/ sits next to SKILL.md inside the skill
SKILL_MD = Path(__file__).resolve().parents[1] / "SKILL.md"
_VERIFIED_RE = re.compile(r'game-version-verified:\s*"?([\w.]+)"?')


def _verified_version() -> str | None:
    if not SKILL_MD.is_file():
        return None
    m = _VERIFIED_RE.search(SKILL_MD.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Skill/game version staleness check")
    parser.add_argument("--game-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    game_dir = args.game_dir or find_game_dir()
    if game_dir is None or not (game_dir / "launcher-settings.json").is_file():
        print("error: could not locate a HOI4 install (set --game-dir)", file=sys.stderr)
        return 2

    installed = json.loads(
        (game_dir / "launcher-settings.json").read_text(encoding="utf-8-sig")
    ).get("rawVersion", "?")
    verified = _verified_version() or "?"

    if installed == verified:
        print(f"in sync: skill verified against {verified}, install is {installed}")
        return 0

    print(f"STALE: skill verified against {verified}, install is {installed}")
    print("next steps:")
    print(f"  1. python scripts/extract.py                 # refresh data")
    print(
        f"  2. python scripts/version_diff.py extracted/{verified} "
        f"extracted/{installed}"
    )
    print("  3. re-verify claims rows tagged with the old version")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
