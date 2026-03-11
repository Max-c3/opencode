# Local OpenCode + Split MCP Setup

This workspace runs [OpenCode](https://github.com/anomalyco/opencode) locally against 5 MCP servers. This repo owns orchestration only:

- repo-local `opencode.json`
- npm helper scripts
- the generic MCP runtime in `agentic-tools-mcp`

The platform tool logic lives in the sibling monorepo at `/Users/maximilian/coding/agentic-platform-tools`.

## Runtime repo contents

- `/Users/maximilian/coding/opencode`
- `/Users/maximilian/coding/opencode/agentic-tools-mcp`

## Sibling tool monorepo

- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-core`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-ashby`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-gem`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-harmonic`
- `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-metaview`

## What `opencode.json` starts

- `agentic_tools_ashby`
- `agentic_tools_gem`
- `agentic_tools_harmonic`
- `agentic_tools_metaview`
- `linkedin_profile_changes`

Each MCP server runs locally from `/Users/maximilian/coding/opencode/.venv/bin/python`.

## Commands

Bootstrap or refresh the shared Python environment:

```bash
npm run mcp:bootstrap
```

List the configured MCP servers through OpenCode:

```bash
npm run opencode:mcp:list
```

Run the MCP smoke test across the split servers in `mock` mode:

```bash
npm run mcp:smoke
```

Run the live probe for the selected live integrations:

```bash
npm run mcp:probe-live
```

Run OpenCode interactively:

```bash
npm run opencode
```

Run OpenCode non-interactively:

```bash
npm run opencode:run -- "List the available recruiting tools."
```

Start the headless OpenCode server:

```bash
npm run opencode:serve
```

Start the OpenCode web interface:

```bash
npm run opencode:web
```

## Current runtime mode

- Ashby: `live`
- Gem: `live`
- Harmonic: `live`
- Metaview: `mock`

Shared credentials are loaded from `/Users/maximilian/coding/agentic recruiting/.env` via `AR_SHARED_ENV_PATH`.

## Notes

- MCP tool parameters are exposed directly from each tool input schema. They are not wrapped in a top-level `payload` object.
- Gem and Harmonic write tools now execute directly over MCP and return a receipt envelope alongside the business output.
- Receipt and idempotency state persists in `/Users/maximilian/coding/opencode/agentic-tools-mcp/data`.
- Metaview stays in `mock` mode until a real `METAVIEW_API_KEY` is available.
- OpenCode still requires a configured model provider before interactive or non-interactive agent runs will work.
