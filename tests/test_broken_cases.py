"""Broken-case regression suite: every fixture under tests/fixtures/broken/
is a deliberately broken mini-mod with the validator output it MUST produce
(expected.json). Doubles as documentation of what the validator catches —
and of the gaps it does not (cases with "uncaught")."""

import json
from pathlib import Path

import pytest

from tools.validate import validate_mod

BROKEN = Path(__file__).parent / "fixtures" / "broken"
CASES = sorted(p for p in BROKEN.iterdir() if p.is_dir())


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_broken_case(case):
    spec = json.loads((case / "expected.json").read_text(encoding="utf-8"))
    findings = validate_mod(case)
    rules = {f.rule for f in findings}

    for rule in spec.get("expect_rules", []):
        assert rule in rules, f"{case.name}: expected rule {rule}, got {rules}"
    for rule in spec.get("expect_absent_rules", []):
        assert rule not in rules, f"{case.name}: rule {rule} should not fire"

    if "uncaught" in spec:
        # documented gap: nothing fires YET. When a rule starts catching this
        # case, update expected.json and remove the gap note.
        relevant = rules - {"missing-add-namespace"}
        assert not relevant, (
            f"{case.name}: documented as uncaught ({spec['uncaught']}) but "
            f"validator now reports {relevant} — update expected.json"
        )
