"""Read-only MCP server exposing the hoi4-dev-skills tools.

Every tool is a thin wrapper over the tested CLI implementations in
`skills/hoi4-modding/scripts/`. The server is strictly read-only: it can
inspect mods, indexes and logs — it never writes to mods, never launches
the game and never touches the network beyond this stdio connection.

Requires the optional dependency:  pip install "mcp>=2"

Run standalone:  python mcp-server/hoi4_mcp.py
Point an MCP client at this file (see docs/MCP.md).
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SCRIPTS = _REPO / "skills" / "hoi4-modding" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from mcp.server.mcpserver import MCPServer

import doctor as doctor_impl
import error_triage as error_triage_impl
import find as find_impl
import loc_report as loc_report_impl
import validate as validate_impl
from extract import find_game_dir
from chain_map import build_graph as _chain_graph
from override_audit import audit_overrides as _audit_overrides
from stale_check import main as _stale_check_main

mcp = MCPServer(
    "hoi4-dev-skills",
    description=(
        "Read-only Hearts of Iron IV mod auditing: static validation, "
        "identifier tracing, event chains, vanilla override inventory, "
        "localisation coverage, log triage and version staleness. "
        "Inspection only — this server never writes to mods or launches "
        "the game."
    ),
)


def _to_json(obj) -> str:
    return json.dumps(obj, indent=1, ensure_ascii=False, default=str)


@mcp.tool()
def validate_mod(mod_dir: str, data_dir: str = "", game_dir: str = "") -> str:
    """Static-lint a mod: brace/quote balance, duplicate event and focus
    ids, missing localisation keys, unknown effects/ideas/sprites/hooks,
    vanilla override awareness. Returns the findings as JSON."""
    findings = validate_impl.validate_mod(
        Path(mod_dir),
        data_dir=Path(data_dir) if data_dir else None,
        game_dir=Path(game_dir) if game_dir else None,
    )
    return _to_json([
        {"severity": f.severity, "rule": f.rule, "file": f.file,
         "line": f.line, "message": f.message}
        for f in findings
    ])


@mcp.tool()
def doctor(mod_dir: str, out: str = "") -> str:
    """One-shot mod health report: validator + duplicate identifier audit
    + vanilla override inventory + localisation coverage, with a 0-100
    health score. Returns the full report as JSON."""
    report = doctor_impl.build_report(Path(mod_dir))
    return _to_json(report)


@mcp.tool()
def find_identifier(pattern: str, mod_dir: str, game_dir: str = "") -> str:
    """Where is an event/focus/idea/decision/character id defined?
    Substring match over the mod (and vanilla when game_dir is given)."""
    index = find_impl.index_mod(Path(mod_dir),
                                Path(game_dir) if game_dir else None)
    return _to_json(find_impl.lookup(index, pattern))


@mcp.tool()
def event_chain_map(mod_dir: str) -> str:
    """Event firing graph: which events fire which, plus every dangling
    target (fired event with no definition)."""
    return _to_json(_chain_graph(Path(mod_dir)))


@mcp.tool()
def loc_coverage(mod_dir: str) -> str:
    """Localisation coverage per language: keys present in english but
    missing from other language folders (the game falls back silently)."""
    return _to_json(loc_report_impl.report(Path(mod_dir)))


@mcp.tool()
def vanilla_overrides(mod_dir: str, game_dir: str) -> str:
    """Which mod files exactly shadow vanilla files — every one is a
    future patch-break that must be refreshed."""
    return _to_json(_audit_overrides(Path(mod_dir), Path(game_dir)))


@mcp.tool()
def triage_error_log(log_path: str, baseline_path: str = "") -> str:
    """Classify a game error.log; with a baseline, report per-class deltas
    (negative = fixed, positive = introduced)."""
    errors = error_triage_impl.parse_log(Path(log_path))
    if baseline_path:
        baseline = error_triage_impl.parse_log(Path(baseline_path))
        return _to_json({
            "delta": error_triage_impl.diff(baseline, errors),
            "groups": [
                {"class": cls, "message": msg, "delta": d}
                for (cls, msg), d in sorted(
                    error_triage_impl.diff_groups(baseline, errors).items(),
                    key=lambda kv: kv[1])
            ],
        })
    buckets = error_triage_impl.classify(errors)
    return _to_json({c: len(v) for c, v in buckets.items()})


@mcp.tool()
def staleness_check() -> str:
    """Is the skill's verified game version still the installed one?
    Returns the installed and verified versions (run the version_diff
    CLI yourself when they differ — this tool stays read-only)."""
    game_dir = find_game_dir()
    if game_dir is None or not (game_dir / "launcher-settings.json").is_file():
        return _to_json({"error": "no HOI4 install located"})
    installed = json.loads(
        (game_dir / "launcher-settings.json").read_text(encoding="utf-8-sig")
    ).get("rawVersion", "?")
    verified = _stale_verified()
    return _to_json({
        "installed": installed,
        "skill_verified": verified,
        "stale": installed != verified,
    })


def _stale_verified() -> str:
    text = (_REPO / "skills" / "hoi4-modding" / "SKILL.md").read_text(
        encoding="utf-8")
    m = re.search(r'game-version-verified:\s*"?([\w.]+)"?', text)
    return m.group(1) if m else "?"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
