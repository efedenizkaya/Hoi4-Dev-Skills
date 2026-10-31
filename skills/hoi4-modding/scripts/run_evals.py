"""Eval harness: grade mod directories against eval definitions.

`evals/task-evals.json` lists tasks; each entry points at a mod directory
(either a shipped gold solution or an agent's output) and the expectations
it must meet. The harness runs scripts/validate.py's rules and reports
PASS/FAIL per eval.

Usage:
    python tools/run_evals.py --evals evals/task-evals.json [--self-test]

Expectation keys (all optional):
    max_errors       — maximum error-severity findings (default 0)
    max_warnings     — maximum warning-severity findings (default unlimited)
    forbidden_rules  — rules that must NOT appear

Exit codes: 0 = all PASS, 1 = any FAIL, 2 = usage error.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import json
import sys
from pathlib import Path

from validate import validate_mod


def _check(entry: dict, game_dir: Path | None) -> tuple[bool, list[str]]:
    expect = entry.get("expect", {})
    mod_dir = Path(entry["mod_dir"])
    findings = validate_mod(mod_dir, game_dir=game_dir)
    problems: list[str] = []

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    rules = {f.rule for f in findings}

    max_errors = expect.get("max_errors", 0)
    if len(errors) > max_errors:
        problems.append(
            f"{len(errors)} errors (max {max_errors}): "
            + "; ".join(f"{f.rule} {f.file}" for f in errors[:5])
        )
    max_warnings = expect.get("max_warnings")
    if max_warnings is not None and len(warnings) > max_warnings:
        problems.append(f"{len(warnings)} warnings (max {max_warnings})")
    for rule in expect.get("forbidden_rules", []):
        if rule in rules:
            problems.append(f"forbidden rule fired: {rule}")
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grade mod dirs against evals")
    parser.add_argument("--evals", type=Path, required=True)
    parser.add_argument(
        "--self-test", action="store_true",
        help="verify every eval's own mod_dir satisfies its expectations",
    )
    parser.add_argument(
        "--game-dir", type=Path, default=None,
        help="opt-in vanilla awareness (deterministic without it)",
    )
    args = parser.parse_args(argv)

    if not args.evals.is_file():
        print(f"error: {args.evals} not found", file=sys.stderr)
        return 2
    evals = json.loads(args.evals.read_text(encoding="utf-8"))
    if not evals:
        print("error: no evals defined", file=sys.stderr)
        return 2

    game_dir = args.game_dir if args.game_dir is not None and args.game_dir.is_dir() else None
    failures = 0
    for entry in evals:
        name = entry.get("name", entry.get("mod_dir", "?"))
        ok, problems = _check(entry, game_dir)
        if args.self_test:
            # in self-test mode, gold dirs MUST pass their own gates;
            # failing entries that document expected failure stay honest
            if ok:
                print(f"PASS {name}")
            else:
                print(f"FAIL {name}: " + "; ".join(problems))
                failures += 1
        else:
            if ok:
                print(f"PASS {name}")
            else:
                print(f"FAIL {name}: " + "; ".join(problems))
                failures += 1
    print(f"\n{len(evals) - failures}/{len(evals)} eval(s) passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
