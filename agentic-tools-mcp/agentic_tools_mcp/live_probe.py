from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from agentic_tools_core.integration_clients.exceptions import IntegrationConfigError
from agentic_tools_gem.client import build_gem_client
from agentic_tools_harmonic.client import build_harmonic_client
from agentic_tools_mcp.env_loader import load_shared_env
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = MCP_ROOT.parent
PYTHON = str(RUNTIME_ROOT / ".venv" / "bin" / "python")


def _live_env() -> dict[str, str]:
    env = dict(os.environ)
    env["AR_INTEGRATION_MODE"] = "live"
    configured = os.getenv("AR_SHARED_ENV_PATH", "").strip()
    if configured:
        env["AR_SHARED_ENV_PATH"] = configured
    return env


async def _probe_ashby() -> dict[str, Any]:
    server = StdioServerParameters(
        command=PYTHON,
        args=["-m", "agentic_tools_mcp.servers.ashby"],
        env=_live_env(),
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "ashby_get_recent_hires",
                {
                    "count": 1,
                    "selection_mode": "global_latest_best_effort",
                    "sort_by": "hired_at",
                    "sort_order": "desc",
                    "retrieval_policy": "fast_sample",
                    "max_scan_pages": 2,
                },
            )
            payload = dict(result.structuredContent)
            output = payload.get("output", {})
            diagnostics = output.get("diagnostics", {}) if isinstance(output, dict) else {}
            return {
                "status": "ok",
                "tool": "ashby_get_recent_hires",
                "summary": payload.get("summary", ""),
                "returned_count": diagnostics.get("returned_count", 0),
                "stop_reason": diagnostics.get("stop_reason", ""),
            }


def _probe_direct_live_clients() -> dict[str, Any]:
    env_path = load_shared_env()
    os.environ["AR_INTEGRATION_MODE"] = "live"

    status: dict[str, Any] = {
        "env_file": str(env_path) if env_path else "",
    }

    gem_client = build_gem_client("live")
    status["gem"] = {
        "status": "client_ready",
        "client_type": type(gem_client).__name__,
    }

    harmonic_client = build_harmonic_client("live")
    status["harmonic"] = {
        "status": "client_ready",
        "client_type": type(harmonic_client).__name__,
    }

    metaview_key = os.getenv("METAVIEW_API_KEY", "").strip()
    if metaview_key:
        status["metaview"] = {
            "status": "credentials_present",
            "note": "This workspace still starts Metaview in mock mode.",
        }
    else:
        status["metaview"] = {
            "status": "mock_only",
            "reason": "METAVIEW_API_KEY is not set in the shared env file.",
        }

    return status


async def main() -> None:
    client_status = _probe_direct_live_clients()
    ashby_status = await _probe_ashby()
    report = {
        "env_file": client_status.pop("env_file", ""),
        "ashby": ashby_status,
        **client_status,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except IntegrationConfigError as exc:
        raise SystemExit(f"Live probe failed: {exc}") from exc
