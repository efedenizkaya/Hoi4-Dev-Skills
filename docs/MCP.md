# Optional MCP server (read-only)

A thin read-only MCP server over the same tested implementations the CLIs
use. Inspection only: **no mod writes, no game launch, no network beyond
the stdio connection.**

## Install

```bash
pip install "mcp>=2"
```

## Tools exposed

| Tool | Wraps | Read-only over |
|---|---|---|
| `validate_mod` | scripts/validate.py | a mod directory |
| `doctor` | scripts/doctor.py | health report + score |
| `find_identifier` | scripts/find.py | mod + vanilla identifier index |
| `event_chain_map` | scripts/chain_map.py | event firing graph |
| `loc_coverage` | scripts/loc_report.py | language folders |
| `vanilla_overrides` | scripts/override_audit.py | mod vs vanilla shadows |
| `triage_error_log` | scripts/error_triage.py | error.log (+ baseline diff) |
| `staleness_check` | scripts/stale_check.py | installed vs verified version |

## Client configuration

Claude Desktop / Cursor / any MCP client (stdio server):

```json
{
  "mcpServers": {
    "hoi4-dev-skills": {
      "command": "python",
      "args": ["<path-to-repo>/mcp-server/hoi4_mcp.py"]
    }
  }
}
```

## Security boundaries

- Tools accept paths and return JSON. They do not execute mod content,
  launch the game, write files or open network connections.
- The server runs with YOUR user account and can read anything that
  account can read — point it only at paths you intend to expose.
- Prompt-injection stance: mod content returned by these tools is data;
  see [agent-safety.md](../skills/hoi4-modding/references/agent-safety.md).
