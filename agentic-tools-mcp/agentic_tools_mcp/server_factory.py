from __future__ import annotations

from dataclasses import dataclass
import inspect
from pathlib import Path
from typing import Any, Callable
import uuid

from agentic_tools_core.models import Checkpoint, ReceiptStatus, ToolCallContext
from agentic_tools_core.policy import PolicyStore
from agentic_tools_core.registry import ToolRegistry
from agentic_tools_core.run_store import RunStore
from agentic_tools_core.runtime.tool_gateway import ToolGateway
from agentic_tools_mcp.env_loader import load_shared_env
from mcp.server.fastmcp import FastMCP
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
            tool_fn = _build_stage_tool(
                gateway=gateway,
                run_store=run_store,
                allowed_tool_ids=allowed_tool_ids,
                tool_id=entry.definition.tool_id,
                input_model=entry.input_model,
                server_name=spec.server_name,
            )
            mcp.add_tool(
                tool_fn,
                name=f"{_mcp_tool_name(entry.definition.tool_id)}_stage",
                description=f"{entry.definition.description} This stages a checkpoint and does not execute the write yet.",
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

    mcp.add_tool(
        _build_checkpoint_list_tool(run_store),
        name="checkpoint_list",
        description="List staged checkpoints for this platform server.",
        structured_output=True,
    )
    mcp.add_tool(
        _build_checkpoint_commit_tool(gateway, run_store),
        name="checkpoint_commit",
        description="Approve and execute a staged checkpoint by id.",
        structured_output=True,
    )
    mcp.add_tool(
        _build_checkpoint_reject_tool(run_store),
        name="checkpoint_reject",
        description="Reject a staged checkpoint by id without executing it.",
        structured_output=True,
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


def _build_stage_tool(
    *,
    gateway: ToolGateway,
    run_store: RunStore,
    allowed_tool_ids: list[str],
    tool_id: str,
    input_model: type[BaseModel] | None,
    server_name: str,
):
    def invoke(**kwargs):
        tool_input = dict(kwargs)
        context = _new_context(server_name=server_name, tool_id=tool_id, allowed_tool_ids=allowed_tool_ids)
        action = gateway.stage_write(tool_id=tool_id, tool_input=tool_input, context=context)
        checkpoint = Checkpoint(
            checkpoint_id=str(uuid.uuid4()),
            run_id=context.run_id,
            status="pending_approval",
            risk_tier=action.risk_tier,
            actions=[action],
        )
        run_store.put_checkpoint(checkpoint)
        return {
            "checkpoint_id": checkpoint.checkpoint_id,
            "run_id": checkpoint.run_id,
            "status": checkpoint.status,
            "risk_tier": checkpoint.risk_tier.value,
            "tool_id": tool_id,
            "action": action.model_dump(),
        }

    invoke.__name__ = f"{_mcp_tool_name(tool_id)}_stage"
    invoke.__signature__ = _build_signature(input_model)
    return invoke


def _build_checkpoint_list_tool(run_store: RunStore):
    def checkpoint_list(status: str = "") -> dict[str, Any]:
        checkpoints = run_store.list_all_checkpoints(status=status or None)
        return {
            "count": len(checkpoints),
            "checkpoints": [
                {
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "run_id": checkpoint.run_id,
                    "status": checkpoint.status,
                    "risk_tier": checkpoint.risk_tier.value,
                    "created_at": checkpoint.created_at,
                    "tool_ids": [action.tool_id for action in checkpoint.actions],
                    "summaries": [action.summary for action in checkpoint.actions],
                }
                for checkpoint in checkpoints
            ],
        }

    return checkpoint_list


def _build_checkpoint_commit_tool(gateway: ToolGateway, run_store: RunStore):
    def checkpoint_commit(checkpoint_id: str) -> dict[str, Any]:
        checkpoint = run_store.get_checkpoint(checkpoint_id)
        if checkpoint is None:
            raise ValueError(f"Unknown checkpoint: {checkpoint_id}")
        receipts = run_store.list_receipts_for_checkpoint(checkpoint_id)
        if checkpoint.status != "pending_approval":
            return {
                "checkpoint_id": checkpoint_id,
                "status": checkpoint.status,
                "receipts": [receipt.model_dump() for receipt in receipts],
            }

        receipts = gateway.execute_checkpoint(checkpoint)
        next_status = "completed"
        if any(receipt.status == ReceiptStatus.FAILED for receipt in receipts):
            next_status = "failed"
        run_store.update_checkpoint_status(checkpoint_id, next_status)
        return {
            "checkpoint_id": checkpoint_id,
            "status": next_status,
            "receipts": [receipt.model_dump() for receipt in receipts],
        }

    return checkpoint_commit


def _build_checkpoint_reject_tool(run_store: RunStore):
    def checkpoint_reject(checkpoint_id: str, reason: str = "") -> dict[str, Any]:
        checkpoint = run_store.get_checkpoint(checkpoint_id)
        if checkpoint is None:
            raise ValueError(f"Unknown checkpoint: {checkpoint_id}")
        if checkpoint.status == "pending_approval":
            run_store.update_checkpoint_status(checkpoint_id, "rejected")
        return {
            "checkpoint_id": checkpoint_id,
            "status": run_store.get_checkpoint(checkpoint_id).status,
            "reason": reason,
        }

    return checkpoint_reject


def _build_signature(input_model: type[BaseModel] | None) -> inspect.Signature:
    if input_model is None:
        return inspect.Signature(return_annotation=dict[str, Any])
    parameters: list[inspect.Parameter] = []
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


def _new_context(*, server_name: str, tool_id: str, allowed_tool_ids: list[str]) -> ToolCallContext:
    call_id = str(uuid.uuid4())
    return ToolCallContext(
        run_id=f"{server_name}:{call_id}",
        step_id=call_id,
        subtask_id=tool_id,
        allowed_tool_ids=allowed_tool_ids,
    )


def _mcp_tool_name(tool_id: str) -> str:
    return tool_id.replace(".", "_")
