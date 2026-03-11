from __future__ import annotations

from agentic_tools_mcp.servers.ashby import mcp as ashby_mcp
from agentic_tools_mcp.servers.gem import mcp as gem_mcp


def _tool(server, name: str):
    for tool in server._tool_manager.list_tools():
        if tool.name == name:
            return tool
    raise AssertionError(f"missing tool: {name}")


def _tool_names(server) -> set[str]:
    return {tool.name for tool in server._tool_manager.list_tools()}


def test_read_tool_parameters_are_flattened() -> None:
    tool = _tool(ashby_mcp, "ashby_get_recent_hires")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "count" in tool.parameters.get("properties", {})
    assert tool.parameters["properties"]["count"]["maximum"] == 100


def test_write_tool_parameters_are_flattened() -> None:
    tool = _tool(gem_mcp, "gem_create_project")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "project_name" in tool.parameters.get("properties", {})
    assert "project_name" in tool.parameters.get("required", [])


def test_gem_read_tool_parameters_are_flattened() -> None:
    tool = _tool(gem_mcp, "gem_list_project_candidates")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "project_id" in tool.parameters.get("properties", {})
    assert "project_id" in tool.parameters.get("required", [])


def test_new_gem_read_tool_parameters_are_flattened() -> None:
    tool = _tool(gem_mcp, "gem_find_candidates")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "email" in tool.parameters.get("properties", {})
    assert "candidate_ids" in tool.parameters.get("properties", {})


def test_new_gem_write_tool_parameters_are_flattened() -> None:
    tool = _tool(gem_mcp, "gem_update_project")
    assert "payload" not in tool.parameters.get("properties", {})
    assert "project_id" in tool.parameters.get("properties", {})
    assert "project_id" in tool.parameters.get("required", [])


def test_no_checkpoint_tools_are_registered() -> None:
    tool_names = _tool_names(gem_mcp)
    assert "checkpoint_list" not in tool_names
    assert "checkpoint_commit" not in tool_names
    assert "checkpoint_reject" not in tool_names
