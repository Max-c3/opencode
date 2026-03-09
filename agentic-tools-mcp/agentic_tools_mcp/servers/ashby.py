from __future__ import annotations

from pathlib import Path

import agentic_tools_ashby
from agentic_tools_ashby import register_tools

from agentic_tools_mcp.server_factory import ServerSpec, build_server

MCP_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(agentic_tools_ashby.__file__).resolve().parents[1]

mcp = build_server(
    ServerSpec(
        server_name="agentic-tools-ashby",
        platform_name="ashby",
        instructions="Expose all Ashby recruiting tools over MCP in mock or live mode.",
        register_tools=register_tools,
        policy_path=REPO_ROOT / "policy" / "capabilities.yaml",
        db_path=MCP_ROOT / "data" / "ashby.db",
    )
)


if __name__ == "__main__":
    mcp.run(transport="stdio")
