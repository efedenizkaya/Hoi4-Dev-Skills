"""Triage HOI4 ``error.log`` files: parse, classify, and diff two runs.

The game writes ``logs/error.log`` on every launch. The verification loop
for a mod change is: capture a baseline log, apply the change, launch with
``-debug`` again, then diff — this tool turns that diff into a short,
classified answer ("the loc error is gone, one new invalid-tech appeared")
instead of a wall of raw lines.

Usage:
    python tools/error_triage.py <error.log> [--against <baseline.log>]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_LINE_RE = re.compile(r"^\[(\d\d:\d\d:\d\d)\]\[([^\]]+)\](?:\[([^\]]+)\])?:\s(.*)$")

# (compiled pattern, class name) — first match wins. Ordered most-specific
# first. Extend via contributing; keep the registry flat and data-driven.
CLASSIFICATION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"invalid database object", re.I), "invalid-database-object"),
    (re.compile(r"set_technology: Invalid tech", re.I), "invalid-tech"),
    (re.compile(r"Invalid Scope", re.I), "invalid-scope"),
    (re.compile(r"as scope, but could not find", re.I), "invalid-scope"),
    (re.compile(r"does not exist", re.I), "missing-entity"),
    (re.compile(r"localisation|localization", re.I), "loc-error"),
    (re.compile(r"Invalid (?:id|name|key|focus|decision|idea|country tag)", re.I), "invalid-id"),
]


@dataclass
class LogError:
    time: str
    date: str
    source: str
    message: str


def _classify_one(message: str) -> str:
    for pattern, name in CLASSIFICATION_PATTERNS:
        if pattern.search(message):
            return name
    return "other"


def parse_log(path: Path) -> list[LogError]:
    errors: list[LogError] = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        m = _LINE_RE.match(line)
        if m:
            time, date, source, message = m.groups()
            errors.append(LogError(time, date, source or "unknown", message))
    return errors


def classify(errors: list[LogError]) -> dict[str, list[LogError]]:
    buckets: dict[str, list[LogError]] = {}
    for e in errors:
        buckets.setdefault(_classify_one(e.message), []).append(e)
    return buckets


_FILE_LINE_NOISE = re.compile(r"([\w \-]+\.(?:txt|cpp|lua|gui|gfx|yml)):\d+")


def _group_key(e: LogError) -> tuple[str, str]:
    """Identity of an error across runs: class + message with file:line
    numbers normalized. Digits *inside* the message body (e.g. loc key
    names, tech ids) are significant and stay — only the ``file.txt:123``
    prefix churns between runs."""
    normalized = _FILE_LINE_NOISE.sub(r"\1:#", e.message)
    return (_classify_one(e.message), normalized)


def diff_groups(
    before: list[LogError], after: list[LogError]
) -> dict[tuple[str, str], int]:
    """Per-group count delta between two runs (negative = improved)."""
    from collections import Counter

    b = Counter(_group_key(e) for e in before)
    a = Counter(_group_key(e) for e in after)
    return {
        key: a.get(key, 0) - b.get(key, 0)
        for key in set(b) | set(a)
        if a.get(key, 0) != b.get(key, 0)
    }


def diff(before: list[LogError], after: list[LogError]) -> dict[str, int]:
    """Per-class count delta between two runs (negative = improved).
    Includes every class seen in either run, even when its net is zero."""
    from collections import Counter

    b = Counter(_group_key(e)[0] for e in before)
    a = Counter(_group_key(e)[0] for e in after)
    return {cls: a.get(cls, 0) - b.get(cls, 0) for cls in set(b) | set(a)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify and diff HOI4 error logs")
    parser.add_argument("log", type=Path)
    parser.add_argument("--against", type=Path, default=None, help="baseline log")
    args = parser.parse_args(argv)

    errors = parse_log(args.log)
    if not errors:
        print("no parseable errors found — clean log?")
        return 0

    if args.against:
        baseline = parse_log(args.against)
        delta = diff(baseline, errors)
        print(f"{'class':28s} delta")
        for cls, d in sorted(delta.items(), key=lambda kv: kv[1]):
            print(f"{cls:28s} {d:+d}")
        groups = diff_groups(baseline, errors)
        if groups:
            print("\nchanged groups:")
            for (cls, msg), d in sorted(groups.items(), key=lambda kv: kv[1]):
                print(f"  {d:+d}  [{cls}] {msg[:80]}")
        return 0

    buckets = classify(errors)
    print(f"{'class':28s} count  first example")
    for cls in sorted(buckets, key=lambda c: -len(buckets[c])):
        example = buckets[cls][0].message[:70]
        print(f"{cls:28s} {len(buckets[cls]):5d}  {example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
