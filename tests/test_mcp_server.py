"""MCP server tool functions (read-only wrappers over the CLIs).

The server module is imported via importlib from mcp-server/; tests call
the underlying tool functions directly — no MCP transport involved."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp-server" / "hoi4_mcp.py"

pytest.importorskip("mcp", reason="optional mcp dependency not installed")


def _load():
    spec = importlib.util.spec_from_file_location("_hoi4_mcp_test", SERVER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def srv():
    return _load()


MINI = Path(__file__).parent / "fixtures" / "mini_mod"
FAKE_GAME = Path(__file__).parent / "fixtures" / "fake_game"


def test_validate_tool_returns_findings(srv):
    data = json.loads(srv.validate_mod(str(MINI)))
    rules = {f["rule"] for f in data}
    assert "duplicate-event-id" in rules
    assert {"severity", "rule", "file", "message"} <= set(data[0])


def test_find_identifier_tool(srv):
    data = json.loads(srv.find_identifier("ger_test", str(MINI)))
    assert any(m["id"] == "ger_test.1" for m in data)


def test_loc_coverage_tool(srv, tmp_path):
    loc = tmp_path / "localisation"
    (loc / "english").mkdir(parents=True)
    (loc / "english" / "a_l_english.yml").write_bytes(
        b"\xef\xbb\xbf" + b'l_english:\n only.key:0 "x"\n')
    (loc / "german").mkdir()
    (loc / "german" / "a_l_german.yml").write_bytes(
        b"\xef\xbb\xbf" + b'l_german:\n other.key:0 "y"\n')
    data = json.loads(srv.loc_coverage(str(tmp_path)))
    assert data["languages"]["german"]["missing_count"] == 1


def test_triage_tool_no_baseline(srv):
    log = Path(__file__).parent / "fixtures" / "error_before.log"
    data = json.loads(srv.triage_error_log(str(log)))
    assert data.get("invalid-database-object") == 3


def test_stale_verified_reads_skill(srv):
    assert srv._stale_verified() == "1.19.4.1"


def test_server_registers_tools(srv):
    import asyncio

    tools = asyncio.run(srv.mcp.list_tools())
    names = {t.name for t in tools}
    assert {"validate_mod", "doctor", "find_identifier", "event_chain_map",
            "loc_coverage", "vanilla_overrides", "triage_error_log",
            "staleness_check"} <= names
