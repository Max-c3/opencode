# agentic-tools-mcp

Generic MCP runtime for the split recruiting tool repos.

## What this repo does

- loads shared credentials from `AR_SHARED_ENV_PATH` or a known local `.env`
- builds MCP tools automatically from the platform registries
- exposes read tools directly over MCP
- exposes write and side-effect tools directly over MCP
- persists receipt and idempotency state in `data/*.db`

## Server entrypoints

- `python -m agentic_tools_mcp.servers.ashby`
- `python -m agentic_tools_mcp.servers.gem`
- `python -m agentic_tools_mcp.servers.harmonic`
- `python -m agentic_tools_mcp.servers.metaview`

## Tool surface

The server factory inspects each tool's Pydantic input model and generates a flattened MCP signature. Example:

- tool id: `ashby.get_recent_hires`
- MCP name: `ashby_get_recent_hires`
- call shape: direct keyword args such as `count=3`, not `payload={...}`

Write tools use the same naming convention and return:

- `output`: committed business result
- `summary`: short execution summary
- `verification`: runtime verification result
- `receipt`: receipt metadata with `receipt_id`, `tool_id`, `status`, `idempotency_key`, and `created_at`

## Commands

Bootstrap the local runtime virtualenv and editable installs:

```bash
./scripts/bootstrap_local_env.sh
```

Run unit tests:

```bash
../.venv/bin/pytest -q
```

Run the mock smoke test:

```bash
../.venv/bin/python -m agentic_tools_mcp.smoke_test
```

Run the live probe:

```bash
../.venv/bin/python -m agentic_tools_mcp.live_probe
```

## Runtime notes

- This package is expected to live inside `/Users/maximilian/coding/opencode/agentic-tools-mcp`.
- The runtime Python environment lives at `/Users/maximilian/coding/opencode/.venv`.
- Receipt state lives in `/Users/maximilian/coding/opencode/agentic-tools-mcp/data`.
- Ashby, Gem, and Harmonic can run in `live` mode when credentials are present.
- Metaview is currently expected to remain `mock` until a real `METAVIEW_API_KEY` is provided.
