# AGENTS.md

## Project Overview

Local workspace for running [Crush](https://github.com/charmbracelet/crush) with a split MCP setup. OpenCode is not a fork of Crush and does not contain tool business logic. This repo owns runtime/orchestration:

- the upstream `@charmland/crush` dependency
- `crush.json`
- npm helper scripts
- the generic MCP runtime package in `/Users/maximilian/coding/opencode/agentic-tools-mcp`

The platform tool code lives in the sibling monorepo:

- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-core`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-ashby`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-gem`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-harmonic`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-metaview`

## Commands

| Task | Command | Notes |
|---|---|---|
| Launch Crush (interactive) | `npm run crush` | First run requires provider/API key setup |
| Run Crush non-interactively | `npm run crush:run -- "prompt"` | Fails with `No providers configured` if no key set |
| Bootstrap shared Python env | `npm run mcp:bootstrap` | Creates/refreshes `/Users/maximilian/coding/opencode/.venv` and editable installs |
| MCP smoke test | `npm run mcp:smoke` | Runs the split-server smoke test in `mock` mode |
| Live integration probe | `npm run mcp:probe-live` | Verifies current live wiring for Ashby, Gem, and Harmonic |
| Tests | `pytest -q` in the split Python repos | `opencode` itself has no local test suite |

## Project Structure

```
opencode/
├── crush.json                          # Crush config — registers 4 MCP stdio servers
├── package.json                        # npm workspace; pins @charmland/crush@0.47.2
├── agentic-tools-mcp/                   # Generic MCP runtime package
├── tools.md                            # Current callable MCP tools, inputs, and outputs
├── scripts/
│   ├── run_mcp_smoke.sh                # Shell wrapper for mock smoke test
│   └── run_mcp_live_probe.sh           # Shell wrapper for live probe
└── README.md
```

## MCP Runtime

`crush.json` starts 4 MCP servers from `/Users/maximilian/coding/opencode/.venv/bin/python`:

- `agentic_tools_ashby`
- `agentic_tools_gem`
- `agentic_tools_harmonic`
- `agentic_tools_metaview`

Each server is implemented in `/Users/maximilian/coding/opencode/agentic-tools-mcp/agentic_tools_mcp/servers`.

## Environment Variables

| Variable | Purpose |
|---|---|
| `AR_INTEGRATION_MODE` | Selects `mock` or `live` behavior for a server process |
| `AR_SHARED_ENV_PATH` | Shared `.env` file loaded by the MCP server before tool registration |

Current `crush.json` wiring:

- Ashby: `live`
- Gem: `live`
- Harmonic: `live`
- Metaview: `mock`

The shared env file currently points at `/Users/maximilian/coding/agentic recruiting/.env`.

## Key Patterns

- **OpenCode is orchestration only**: no tool-specific MCP server code should live here.
- **Split repos are source-of-truth**: tool contracts and runtime behavior live in the platform repos plus `agentic-tools-core`.
- **Direct MCP parameters**: MCP tools expose flattened parameters derived from each tool input schema, not a top-level `payload`.
- **Checkpointed writes**: Gem write tools and Harmonic enrichment tools stage first, then require `checkpoint_commit`.
- **Persistent run state**: checkpoint and receipt data live in `/Users/maximilian/coding/opencode/agentic-tools-mcp/data`.
- **Tool docs must stay current**: whenever a new callable tool is added, removed, renamed, or its inputs or outputs change, update `tools.md` in the same change. No new tool should ship without concise documentation of what it does, its inputs, and its outputs.

## Gotchas

1. **The sibling tool monorepo must exist locally**: `crush`, smoke tests, and live probes depend on `/Users/maximilian/coding/agentic-platform-tools`.
2. **`crush.json` still uses absolute paths**: if this repo moves, update the Python interpreter path there.
3. **Provider setup required**: Crush itself still requires a configured model provider.
4. **Metaview is intentionally mock-only right now**: there is no usable `METAVIEW_API_KEY` in the shared env file.
5. **The smoke test is mock by design**: use `npm run mcp:probe-live` when you need to confirm live credential wiring.
