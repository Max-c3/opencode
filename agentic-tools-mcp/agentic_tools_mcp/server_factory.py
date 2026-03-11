from __future__ import annotations

from dataclasses import dataclass
import inspect
from pathlib import Path
from typing import Any, Callable
import uuid

from agentic_tools_core.models import ToolCallContext
from agentic_tools_core.policy import PolicyStore
from agentic_tools_core.registry import ToolRegistry
from agentic_tools_core.run_store import RunStore
from agentic_tools_core.runtime.tool_gateway import ToolGateway
from agentic_tools_mcp.env_loader import load_shared_env
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel


@dataclass(frozen=True)
class ServerSpec:
    server_name: str
    platform_name: str
    instructions: str
    register_tools: Callable[[ToolRegistry], None]
    policy_path: Path
    db_path: Path


def build_server(spec: ServerSpec) -> FastMCP:
    load_shared_env()
    registry = ToolRegistry()
    spec.register_tools(registry)
    policy_store = PolicyStore(spec.policy_path)
    run_store = RunStore(spec.db_path)
    gateway = ToolGateway(policy_store=policy_store, registry=registry, run_store=run_store)

    mcp = FastMCP(spec.server_name, instructions=spec.instructions)
    allowed_tool_ids = [definition.tool_id for definition in registry.list_definitions()]

    for entry in registry.list_registered():
        policy = policy_store.get(entry.definition.tool_id)
        if policy.read_write == "write":
            tool_fn = _build_write_tool(
                gateway=gateway,
                allowed_tool_ids=allowed_tool_ids,
                tool_id=entry.definition.tool_id,
                input_model=entry.input_model,
                server_name=spec.server_name,
            )
            mcp.add_tool(
                tool_fn,
                name=_mcp_tool_name(entry.definition.tool_id),
                description=entry.definition.description,
                structured_output=True,
                meta=_tool_meta(entry.definition, policy.read_write),
            )
            continue

        tool_fn = _build_read_tool(
            gateway=gateway,
            allowed_tool_ids=allowed_tool_ids,
            tool_id=entry.definition.tool_id,
            input_model=entry.input_model,
            server_name=spec.server_name,
        )
        mcp.add_tool(
            tool_fn,
            name=_mcp_tool_name(entry.definition.tool_id),
            description=entry.definition.description,
            structured_output=True,
            meta=_tool_meta(entry.definition, policy.read_write),
        )
    return mcp


def _tool_meta(definition: Any, mode: str) -> dict[str, Any]:
    return {
        "tool_id": definition.tool_id,
        "integration": definition.integration,
        "approval_class": definition.approval_class,
        "read_write": mode,
    }


def _build_read_tool(
    *,
    gateway: ToolGateway,
    allowed_tool_ids: list[str],
    tool_id: str,
    input_model: type[BaseModel] | None,
    server_name: str,
):
    def invoke(**kwargs):
        context = _new_context(server_name=server_name, tool_id=tool_id, allowed_tool_ids=allowed_tool_ids)
        return gateway.execute_read(tool_id=tool_id, tool_input=dict(kwargs), context=context)

    invoke.__name__ = _mcp_tool_name(tool_id)
    invoke.__signature__ = _build_signature(input_model)
    return invoke


def _build_write_tool(
    *,
    gateway: ToolGateway,
    allowed_tool_ids: list[str],
    tool_id: str,
    input_model: type[BaseModel] | None,
    server_name: str,
):
    def invoke(ctx: Context, **kwargs):
        tool_input = dict(kwargs)
        context = _new_context(
            server_name=server_name,
            tool_id=tool_id,
            allowed_tool_ids=allowed_tool_ids,
            request_id=ctx.request_id,
        )
        return gateway.execute_write(tool_id=tool_id, tool_input=tool_input, context=context)

    invoke.__name__ = _mcp_tool_name(tool_id)
    invoke.__signature__ = _build_signature(input_model, include_context=True)
    return invoke


def _build_signature(input_model: type[BaseModel] | None, *, include_context: bool = False) -> inspect.Signature:
    if input_model is None and not include_context:
        return inspect.Signature(return_annotation=dict[str, Any])
    parameters: list[inspect.Parameter] = []
    if include_context:
        parameters.append(
            inspect.Parameter(
                name="ctx",
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Context,
            )
        )
    if input_model is None:
        return inspect.Signature(parameters=parameters, return_annotation=dict[str, Any])
    for field_name, field in input_model.model_fields.items():
        annotation = field.rebuild_annotation()
        default = inspect.Parameter.empty if field.is_required() else field.get_default(call_default_factory=True)
        parameters.append(
            inspect.Parameter(
                name=field.alias or field_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=annotation,
            )
        )
    return inspect.Signature(parameters=parameters, return_annotation=dict[str, Any])


def _new_context(
    *,
    server_name: str,
    tool_id: str,
    allowed_tool_ids: list[str],
    request_id: str = "",
) -> ToolCallContext:
    call_id = request_id or str(uuid.uuid4())
    return ToolCallContext(
        run_id=f"{server_name}:{call_id}",
        step_id=call_id,
        request_id=call_id,
        subtask_id=tool_id,
        allowed_tool_ids=allowed_tool_ids,
    )


def _mcp_tool_name(tool_id: str) -> str:
    return tool_id.replace(".", "_")
