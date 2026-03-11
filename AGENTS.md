# AGENTS.md

## Project Overview

Local workspace for running [OpenCode](https://github.com/anomalyco/opencode) with a split MCP setup. This repo owns orchestration only:

- the repo-local `opencode.json`
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
| Launch OpenCode (interactive) | `npm run opencode` | Requires provider/API key setup |
| Run OpenCode non-interactively | `npm run opencode:run -- "prompt"` | Uses the repo-local `opencode.json` |
| Start headless OpenCode server | `npm run opencode:serve` | Useful for attach or web flows |
| Start OpenCode web interface | `npm run opencode:web` | Starts the server and web UI |
| List configured MCP servers | `npm run opencode:mcp:list` | Verifies the local MCP wiring |
| Bootstrap shared Python env | `npm run mcp:bootstrap` | Creates or refreshes `/Users/maximilian/coding/opencode/.venv` and editable installs |
| MCP smoke test | `npm run mcp:smoke` | Runs the split-server smoke test in `mock` mode |
| Live integration probe | `npm run mcp:probe-live` | Verifies current live wiring for Ashby, Gem, and Harmonic |
| Tests | `pytest -q` in the split Python repos | `opencode` itself has no local test suite |

## Project Structure

```text
opencode/
├── opencode.json                       # OpenCode config — registers 5 local MCP servers
├── package.json                        # npm workspace; pins opencode-ai
├── agentic-tools-mcp/                  # Generic MCP runtime package
├── tools.md                            # Current callable MCP tools, inputs, and outputs
├── scripts/
│   ├── run_mcp_smoke.sh                # Shell wrapper for mock smoke test
│   └── run_mcp_live_probe.sh           # Shell wrapper for live probe
└── README.md
```

## MCP Runtime

`opencode.json` starts 5 MCP servers from `/Users/maximilian/coding/opencode/.venv/bin/python`:

- `agentic_tools_ashby`
- `agentic_tools_gem`
- `agentic_tools_harmonic`
- `agentic_tools_metaview`
- `linkedin_profile_changes`

Each server is implemented in `/Users/maximilian/coding/opencode/agentic-tools-mcp/agentic_tools_mcp/servers` or the linked profile-change package.

## Environment Variables

| Variable | Purpose |
|---|---|
| `AR_INTEGRATION_MODE` | Selects `mock` or `live` behavior for a server process |
| `AR_SHARED_ENV_PATH` | Shared `.env` file loaded by the MCP server before tool registration |

Current `opencode.json` wiring:

- Ashby: `live`
- Gem: `live`
- Harmonic: `live`
- Metaview: `mock`

The shared env file currently points at `/Users/maximilian/coding/agentic recruiting/.env`.

## Key Patterns

- **OpenCode is orchestration only**: no tool-specific MCP server code should live here.
- **Split repos are source-of-truth**: tool contracts and runtime behavior live in the platform repos plus `agentic-tools-core`.
- **Direct MCP parameters**: MCP tools expose flattened parameters derived from each tool input schema, not a top-level `payload`.
- **Direct writes**: Gem write tools and Harmonic enrichment tools execute directly and return receipt metadata with the verified result.
- **Persistent run state**: receipt and idempotency data live in `/Users/maximilian/coding/opencode/agentic-tools-mcp/data`.
- **Tool docs must stay current**: whenever a callable tool is added, removed, renamed, or its inputs or outputs change, update `tools.md` in the same change.

## Gotchas

1. **The sibling tool monorepo must exist locally**: OpenCode, the smoke test, and the live probe depend on `/Users/maximilian/coding/agentic-platform-tools`.
2. **`opencode.json` uses absolute paths**: if this repo moves, update the Python interpreter path there.
3. **Provider setup required**: OpenCode still requires a configured model provider.
4. **Metaview is intentionally mock-only right now**: there is no usable `METAVIEW_API_KEY` in the shared env file.
5. **The smoke test is mock by design**: use `npm run mcp:probe-live` when you need to confirm live credential wiring.
