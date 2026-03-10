from __future__ import annotations

from agentic_tools_mcp.servers.ashby import mcp as ashby_mcp
from agentic_tools_mcp.servers.gem import mcp as gem_mcp


def _tool(server, name: str):
    for tool in server._tool_manager.list_tools():
        if tool.name == name:
            return tool
    raise AssertionError(f"missing tool: {name}")


def test_read_tool_parameters_are_flattened() -> None:
    tool = _tool(ashby_mcp, "ashby_get_recent_hires")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "count" in tool.parameters.get("properties", {})
    assert tool.parameters["properties"]["count"]["maximum"] == 100


def test_write_tool_parameters_are_flattened() -> None:
    tool = _tool(gem_mcp, "gem_create_project_stage")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "project_name" in tool.parameters.get("properties", {})
    assert "project_name" in tool.parameters.get("required", [])


def test_gem_read_tool_parameters_are_flattened() -> None:
    tool = _tool(gem_mcp, "gem_list_project_candidates")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "project_id" in tool.parameters.get("properties", {})
    assert "project_id" in tool.parameters.get("required", [])
