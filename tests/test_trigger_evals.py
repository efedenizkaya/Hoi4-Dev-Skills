"""trigger-evals.json data-quality runner: schema, unique queries, valid
booleans — the data can only be as good as its structure."""

import json
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1] / "evals" / "trigger-evals.json"


def load() -> list[dict]:
    return json.loads(EVALS.read_text(encoding="utf-8"))


def test_schema():
    for entry in load():
        assert set(entry) >= {"query", "should_trigger", "reason"}, entry
        assert isinstance(entry["query"], str) and entry["query"].strip()
        assert isinstance(entry["should_trigger"], bool)
        assert isinstance(entry["reason"], str) and entry["reason"].strip()


def test_queries_unique():
    queries = [e["query"].lower() for e in load()]
    assert len(queries) == len(set(queries)), "duplicate queries"


def test_has_both_classes():
    labels = {e["should_trigger"] for e in load()}
    assert labels == {True, False}, "evals need both trigger and non-trigger examples"
