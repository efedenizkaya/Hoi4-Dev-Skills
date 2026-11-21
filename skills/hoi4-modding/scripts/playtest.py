"""Automated Playtester: structured in-game test definitions + evaluation
of game-run evidence.

The USER launches HOI4 (with -debug). This tool:
- `run`     — runs pre-checks (validator) for each test and prints the
              exact in-game checklist + baseline capture instructions;
              it NEVER launches the game and never counts "game started"
              as a pass.
- `evaluate`— compares baseline vs after error.log via triage diff and
              grades each test against its expectations, writing a
              results file.

Usage:
    python tools/playtest.py run --tests <playtests.json>
    python tools/playtest.py evaluate --tests <f> --id <test_id>
            --baseline <log> --after <log> [--results results.json]

Test entry format:
    {"id": "...", "mod_dir": "...", "description": "...",
     "expect": {"max_errors": N, "forbidden_rules": [...],
                "max_new_errors": N}}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .error_triage import diff, diff_groups, parse_log
    from .validate import validate_mod
except ImportError:
    from error_triage import diff, diff_groups, parse_log
    from validate import validate_mod


def _load_tests(path: Path, test_id: str | None) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tests = data["tests"] if isinstance(data, dict) else data
    if test_id:
        tests = [t for t in tests if t["id"] == test_id]
        if not tests:
            print(f"error: test id '{test_id}' not found", file=sys.stderr)
            sys.exit(2)
    return tests


def cmd_run(args) -> int:
    tests = _load_tests(Path(args.tests), args.id)
    failures = 0
    for t in tests:
        print(f"== {t['id']} — {t.get('description', '')}")
        findings = validate_mod(Path(t["mod_dir"]))
        errors = [f for f in findings if f.severity == "error"]
        if errors:
            failures += 1
            print(f"  PRE-CHECK FAILED: {len(errors)} error(s) — fix before "
                  "launching the game:")
            for f in errors[:10]:
                loc = f"{f.file}:{f.line}" if f.line else f.file
                print(f"    [{f.rule}] {loc}: {f.message}")
        else:
            print("  pre-check clean")
        print("  in-game checklist (user performs):")
        print("    1. copy the current logs/error.log as the baseline")
        print("    2. launch with -debug, reproduce the scenario, quit")
        print("    3. then evaluate: python tools/playtest.py evaluate "
              "--tests <file> --id " + t["id"] +
              " --baseline baseline.log --after logs/error.log")
    return 1 if failures else 0


def evaluate(tests_path: Path, test_id: str | None, baseline_path: Path,
             after_path: Path, results_path: Path | None = None) -> tuple[int, list[dict]]:
    """Grade a game run's evidence; returns (exit_code, results)."""
    tests = _load_tests(Path(tests_path), test_id)
    baseline = parse_log(Path(baseline_path))
    after = parse_log(Path(after_path))
    delta = diff(baseline, after)
    groups = diff_groups(baseline, after)

    results = []
    failures = 0
    for t in tests:
        expect = t.get("expect", {})
        max_new = expect.get("max_new_errors", 0)
        new_errors = sum(max(d, 0) for d in delta.values())
        passed = new_errors <= max_new
        forbidden = [r for r in expect.get("forbidden_rules", [])
                     if any(g["class"] == r for g in groups)]
        if forbidden:
            passed = False
        results.append({
            "id": t["id"],
            "pass": passed,
            "new_errors": new_errors,
            "delta": delta,
            "changed_groups": [
                {"class": cls, "message": msg, "delta": d}
                for (cls, msg), d in sorted(groups.items(), key=lambda kv: kv[1])
            ],
            "forbidden_rule_violations": forbidden,
        })
        if not passed:
            failures += 1

    if results_path:
        Path(results_path).write_text(
            json.dumps(results, indent=1), encoding="utf-8")
    return (1 if failures else 0), results


def cmd_evaluate(args) -> int:
    rc, _ = evaluate(Path(args.tests), args.id, Path(args.baseline),
                     Path(args.after), Path(args.results) if args.results else None)
    return rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Playtest definitions + evaluation")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="pre-checks + in-game checklist")
    p_run.add_argument("--tests", type=Path, required=True)
    p_run.add_argument("--id", default=None)

    p_eval = sub.add_parser("evaluate", help="grade a game run's evidence")
    p_eval.add_argument("--tests", type=Path, required=True)
    p_eval.add_argument("--id", default=None)
    p_eval.add_argument("--baseline", type=Path, required=True)
    p_eval.add_argument("--after", type=Path, required=True)
    p_eval.add_argument("--results", type=Path, default=None)

    args = parser.parse_args(argv)
    return cmd_run(args) if args.cmd == "run" else cmd_evaluate(args)


if __name__ == "__main__":
    raise SystemExit(main())
