# OpenCode Split MCP Runtime

This workspace runs [OpenCode](https://opencode.ai/) locally with four MCP stdio servers for recruiting workflows. It is an orchestration repo, not the source of truth for provider logic.

The active CLI dependency is `opencode-ai`, and the active local config file is `opencode.json`.

This repo owns:

- the pinned `opencode-ai` CLI dependency
- `opencode.json` and npm helper scripts
- the generic MCP runtime in `agentic-tools-mcp`
- the tool reference in [`tools.md`](./tools.md)

The provider-specific tool implementations live in the sibling monorepo at `/Users/maximilian/coding/agentic-platform-tools`.

## How It Works

OpenCode starts local MCP servers from `opencode.json`, each using `/Users/maximilian/coding/opencode/.venv/bin/python` and a module in `agentic_tools_mcp.servers`.

The MCP runtime:

- loads shared credentials from `AR_SHARED_ENV_PATH`, then falls back to `/Users/maximilian/coding/agentic recruiting/.env`, then `./.env`
- registers tools from the sibling platform packages at startup
- exposes read tools with flattened keyword arguments, not a top-level `payload`
- stages write and side-effecting tools as `*_stage`
- persists checkpoint and receipt state in `agentic-tools-mcp/data/*.db`

Current server wiring in `opencode.json`:

| Server | Module | Mode | Notes |
|---|---|---|---|
| `agentic_tools_ashby` | `agentic_tools_mcp.servers.ashby` | `live` | Ashby hiring search, recent hires, and coverage audit tools |
| `agentic_tools_gem` | `agentic_tools_mcp.servers.gem` | `live` | Gem candidate, project, sequence, custom field, and staged write tools |
| `agentic_tools_harmonic` | `agentic_tools_mcp.servers.harmonic` | `live` | Harmonic search, funding, headcount, network, export, and staged enrichment tools |
| `agentic_tools_metaview` | `agentic_tools_mcp.servers.metaview` | `mock` | Metaview profile enrichment; currently configured mock-only in OpenCode |

For the current callable surface, inputs, and outputs, use [`tools.md`](./tools.md).

## Prerequisites

- Node/npm for the `opencode-ai` package
- Python 3.11 for the shared runtime venv
- the sibling monorepo at `/Users/maximilian/coding/agentic-platform-tools`
- a shared env file for live integrations
- an OpenCode model provider configured separately from this repo

Bootstrap defaults:

- `PLATFORM_ROOT` defaults to `../agentic-platform-tools`
- `PYTHON_BIN` defaults to `/opt/homebrew/bin/python3.11`
- `npm run mcp:bootstrap` creates or refreshes `/Users/maximilian/coding/opencode/.venv` and installs the platform packages plus `agentic-tools-mcp` in editable mode

## Quick Start

```bash
npm install
npm run mcp:bootstrap
npm run mcp:smoke
npm run mcp:probe-live
npm run opencode
```

For a non-interactive run:

```bash
npm run opencode:run -- "List the available recruiting tools."
```

## Commands

| Task | Command | What it does |
|---|---|---|
| Install JS deps | `npm install` | Installs the pinned `opencode-ai` CLI |
| Bootstrap Python runtime | `npm run mcp:bootstrap` | Creates `.venv` and editable-installs the MCP runtime plus sibling platform packages |
| Mock end-to-end validation | `npm run mcp:smoke` | Starts all four servers in `mock` mode and exercises read/stage/commit/reject flows |
| Live wiring probe | `npm run mcp:probe-live` | Loads shared credentials, checks Gem and Harmonic live clients, and probes Ashby through the MCP server |
| Run OpenCode interactively | `npm run opencode` | Launches OpenCode with the local MCP config |
| Run OpenCode once | `npm run opencode:run -- "prompt"` | Executes a single prompt non-interactively |
| Runtime unit tests | `./.venv/bin/pytest -q agentic-tools-mcp/tests` | Runs the local MCP runtime tests |

The top-level `npm test` script is only a placeholder. The real local tests in this repo live under `agentic-tools-mcp/tests`.

## Checkpoint Model

Read tools execute immediately. Write and side-effecting tools return a staged checkpoint first.

Typical flow:

1. Call a `*_stage` tool such as `gem_create_project_stage`.
2. Review the returned `checkpoint_id`, preview output, and verification data.
3. Approve with `checkpoint_commit` or discard with `checkpoint_reject`.

Checkpoint tools are available on every server and only operate on checkpoints created by that server.

## Repository Layout

```text
opencode/
├── opencode.json
├── package.json
├── tools.md
├── scripts/
│   ├── run_mcp_smoke.sh
│   └── run_mcp_live_probe.sh
└── agentic-tools-mcp/
    ├── agentic_tools_mcp/
    ├── scripts/bootstrap_local_env.sh
    ├── tests/
    └── README.md
```

## Notes

- `opencode.json` uses absolute paths. If this repo moves, update the Python interpreter path and any env-file paths.
- The current shared env path is `/Users/maximilian/coding/agentic recruiting/.env`.
- Metaview is intentionally started in `mock` mode in OpenCode until a usable `METAVIEW_API_KEY` is available.
- `npm run mcp:smoke` is mock by design and clears local checkpoint DB files before it runs.
- `npm run mcp:probe-live` can take a bit because the Ashby probe uses the real recent-hires MCP path with strict retrieval settings.
- When the tool surface changes, update [`tools.md`](./tools.md) in the same change.
