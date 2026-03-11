from __future__ import annotations

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = MCP_ROOT.parent
PYTHON = str(RUNTIME_ROOT / ".venv" / "bin" / "python")
DATA_DIR = MCP_ROOT / "data"

SERVER_ARGS = {
    "ashby": ["-m", "agentic_tools_mcp.servers.ashby"],
    "gem": ["-m", "agentic_tools_mcp.servers.gem"],
    "harmonic": ["-m", "agentic_tools_mcp.servers.harmonic"],
    "metaview": ["-m", "agentic_tools_mcp.servers.metaview"],
}


def _server(name: str) -> StdioServerParameters:
    return StdioServerParameters(
        command=PYTHON,
        args=SERVER_ARGS[name],
        env={"AR_INTEGRATION_MODE": "mock"},
    )


async def _call(name: str, tool: str, args: dict) -> dict:
    async with stdio_client(_server(name)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, args)
            return dict(result.structuredContent)


async def _list_tools(name: str) -> list[str]:
    async with stdio_client(_server(name)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [tool.name for tool in tools.tools]


async def main() -> None:
    if DATA_DIR.exists():
        for db in DATA_DIR.glob("*.db*"):
            db.unlink()

    ashby_tools = await _list_tools("ashby")
    ashby_result = await _call(
        "ashby",
        "ashby_get_recent_hires",
        {
            "count": 3,
            "selection_mode": "global_latest_exact",
            "sort_by": "hired_at",
            "sort_order": "desc",
            "retrieval_policy": "strict_count",
        },
    )

    gem_tools = await _list_tools("gem")
    gem_write = await _call(
        "gem",
        "gem_create_project",
        {"project_name": "Backend Hiring Sprint", "metadata": {"source": "smoke"}},
    )

    harmonic_tools = await _list_tools("harmonic")
    harmonic_write = await _call(
        "harmonic",
        "harmonic_enrich_person",
        {"linkedin_url": "https://linkedin.com/in/example-person"},
    )

    metaview_tools = await _list_tools("metaview")
    metaview_result = await _call(
        "metaview",
        "metaview_enrich_candidate_profiles",
        {
            "profiles": [
                {
                    "name": "Casey Example",
                    "email": "casey@example.com",
                    "linkedin": "https://linkedin.com/in/casey-example",
                }
            ]
        },
    )

    print("ASHBY_TOOLS", ashby_tools)
    print("ASHBY_RESULT", ashby_result)
    print("GEM_TOOLS", gem_tools)
    print("GEM_WRITE", gem_write)
    print("HARMONIC_TOOLS", harmonic_tools)
    print("HARMONIC_WRITE", harmonic_write)
    print("METAVIEW_TOOLS", metaview_tools)
    print("METAVIEW_RESULT", metaview_result)


if __name__ == "__main__":
    asyncio.run(main())
