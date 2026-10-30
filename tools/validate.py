"""Static validator for HOI4 mods: fast, dependency-free checks.

This is layer one of the verification loop — instant, agent-callable
syntax/consistency checks. It does not replace the game's own judgment
(launch with ``-debug`` and diff ``error.log``) or deep tooling such as
CWTools; it catches the mechanical mistakes first so the expensive checks
run less often.

Usage:
    python tools/validate.py <mod_dir> [--data <extracted_data_dir>]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Paradox script files the rules below apply to, relative to the mod root.
SCRIPT_GLOBS = ["**/*.txt"]
LOC_GLOBS = ["localisation/**/*.yml", "localisation/**/*.yaml"]

_EVENT_ID_RE = re.compile(
    r"\b(country_event|news_event|state_event|unit_leader_event)"
    r"\s*=\s*\{[^{}]*?id\s*=\s*([\w.\-]+)",
    re.S,
)
# Loc refs used by events: title/desc/name = <namespace>.<n>[.<letter>]
_LOC_REF_RE = re.compile(
    r"^\s*(?:title|desc|name)\s*=\s*([A-Za-z][\w]*\.\d+(?:\.[A-Za-z0-9_]+)?)\s*(?:#.*)?$",
    re.M,
)
_LOC_KEY_RE = re.compile(r"^\s*([A-Za-z][\w.\-]*):\d*\s*\"", re.M)


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    rule: str
    file: str
    line: int | None
    message: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def mask_comments_and_strings(text: str) -> str:
    """Return text of equal length with comments and string *contents* blanked.

    Both quote characters of a string are KEPT, so counting quotes in the
    masked text counts unclosed strings: a paired string contributes 2, an
    unclosed one 1 (everything it swallowed was blanked). ``#`` outside a
    string starts a comment (to end of line); inside a string it is literal.
    Blanking instead of deleting preserves line/column data.
    """
    out = list(text)
    in_string = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if in_string:
            if ch == '"':
                in_string = False
            elif ch != "\n":
                out[i] = " "
        else:
            if ch == '"':
                in_string = True
            elif ch == "#":
                while i < n and text[i] != "\n":
                    out[i] = " "
                    i += 1
                continue
        i += 1
    return "".join(out)


def _check_balance(rel: str, text: str, findings: list[Finding]) -> None:
    masked = mask_comments_and_strings(text)
    braces = masked.count("{") - masked.count("}")
    if braces != 0:
        findings.append(
            Finding(
                severity="error",
                rule="unbalanced-braces",
                file=rel,
                line=None,
                message=f"{braces:+d} unmatched brace(s)",
            )
        )
    quotes = masked.count('"')
    if quotes % 2 != 0:
        findings.append(
            Finding(
                severity="error",
                rule="unbalanced-quotes",
                file=rel,
                line=None,
                message=f"{quotes} quote char(s) — odd count",
            )
        )


def _check_duplicate_event_ids(
    mod_dir: Path, findings: list[Finding], game_event_ids: set[str] | None = None
) -> None:
    seen: dict[str, list[tuple[str, int]]] = {}
    for path in sorted(mod_dir.glob("events/*.txt")):
        text = _read(path)
        masked = mask_comments_and_strings(text)
        for m in _EVENT_ID_RE.finditer(masked):
            event_id = m.group(2)
            line = masked.count("\n", 0, m.start(2)) + 1
            seen.setdefault(event_id, []).append((str(path.relative_to(mod_dir)), line))
    for event_id, spots in sorted(seen.items()):
        if len(spots) == 1 and game_event_ids and event_id in game_event_ids:
            # Redefining a base-game event once is the standard way to
            # override it — intentional, so only a warning.
            findings.append(
                Finding(
                    severity="warning",
                    rule="vanilla-event-override",
                    file=spots[0][0],
                    line=spots[0][1],
                    message=f"{event_id}: overrides a base-game event (intentional?)",
                )
            )
        elif len(spots) > 1:
            files = ", ".join(f"{f}:{ln}" for f, ln in spots)
            findings.append(
                Finding(
                    severity="error",
                    rule="duplicate-event-id",
                    file=spots[0][0],
                    line=spots[0][1],
                    message=f"{event_id}: defined {len(spots)} times ({files})",
                )
            )


def _load_event_ids_from(events_dir: Path) -> set[str]:
    ids: set[str] = set()
    if not events_dir.is_dir():
        return ids
    for path in sorted(events_dir.glob("*.txt")):
        masked = mask_comments_and_strings(_read(path))
        ids.update(m.group(2) for m in _EVENT_ID_RE.finditer(masked))
    return ids


def _load_loc_keys(
    mod_dir: Path, findings: list[Finding], game_dir: Path | None = None
) -> set[str]:
    keys: set[str] = set()
    for pattern in LOC_GLOBS:
        for path in mod_dir.glob(pattern):
            raw = path.read_bytes()
            if not raw.startswith(b"\xef\xbb\xbf"):
                findings.append(
                    Finding(
                        severity="warning",
                        rule="loc-file-encoding",
                        file=str(path.relative_to(mod_dir)),
                        line=None,
                        message="localisation file has no UTF-8 BOM (game requires it)",
                    )
                )
            text = raw.decode("utf-8-sig", errors="replace")
            keys.update(_LOC_KEY_RE.findall(text))
    if game_dir is not None:
        # Base-game keys count as defined: mods may reference them when they
        # copy or extend vanilla events. Game files are never BOM-checked.
        # Key sets are identical across language folders, so reading one is
        # enough — `english` when present, everything otherwise.
        game_loc = game_dir / "localisation"
        roots = [game_loc / "english"] if (game_loc / "english").is_dir() else [game_loc]
        for root in roots:
            for path in root.glob("**/*.yml"):
                text = path.read_text(encoding="utf-8-sig", errors="replace")
                keys.update(_LOC_KEY_RE.findall(text))
    return keys


def _check_loc_refs(mod_dir: Path, keys: set[str], findings: list[Finding]) -> None:
    for path in sorted(mod_dir.glob("events/*.txt")):
        text = _read(path)
        masked = mask_comments_and_strings(text)
        rel = str(path.relative_to(mod_dir))
        for m in _LOC_REF_RE.finditer(masked):
            key = m.group(1)
            if key not in keys:
                line = masked.count("\n", 0, m.start()) + 1
                findings.append(
                    Finding(
                        severity="error",
                        rule="missing-loc-key",
                        file=rel,
                        line=line,
                        message=f"{key}: not found in any localisation file",
                    )
                )


def validate_mod(
    mod_dir: Path, data_dir: Path | None = None, game_dir: Path | None = None
) -> list[Finding]:
    """Run all v1 rules over a mod directory and return the findings.

    ``data_dir`` (from tools/extract.py) is reserved for engine-derived rule
    data (e.g. known effect/trigger names); unused in v1. ``game_dir`` (the
    HOI4 install) enables base-game awareness: vanilla loc keys are accepted
    and single re-definitions of vanilla event IDs downgrade to warnings.
    """
    findings: list[Finding] = []
    for pattern in SCRIPT_GLOBS:
        for path in sorted(mod_dir.glob(pattern)):
            if not path.is_file():
                continue
            rel = str(path.relative_to(mod_dir))
            _check_balance(rel, _read(path), findings)

    game_event_ids = _load_event_ids_from(game_dir / "events") if game_dir else None
    _check_duplicate_event_ids(mod_dir, findings, game_event_ids)
    keys = _load_loc_keys(mod_dir, findings, game_dir)
    _check_loc_refs(mod_dir, keys, findings)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Static HOI4 mod validator")
    parser.add_argument("mod_dir", type=Path)
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument(
        "--game-dir",
        type=Path,
        default=None,
        help="HOI4 install root (auto-detected when omitted)",
    )
    parser.add_argument(
        "--no-game", action="store_true", help="skip base-game awareness"
    )
    args = parser.parse_args(argv)

    if not args.mod_dir.is_dir():
        print(f"error: {args.mod_dir} is not a mod directory", file=sys.stderr)
        return 2

    game_dir: Path | None = args.game_dir
    if not args.no_game and game_dir is None:
        try:
            from .extract import find_game_dir
        except ImportError:
            from extract import find_game_dir
        game_dir = find_game_dir()

    findings = validate_mod(args.mod_dir, args.data, game_dir)
    for f in findings:
        loc = f"{f.file}:{f.line}" if f.line is not None else f.file
        print(f"[{f.severity.upper()}] {f.rule} {loc}: {f.message}")
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = len(findings) - errors
    print(f"\n{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
