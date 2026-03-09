# Local Crush + Split MCP Setup

This workspace runs [Crush](https://github.com/charmbracelet/crush) locally via a pinned npm package and uses 4 local MCP servers as tool providers. This repo owns runtime/orchestration only:

- OpenCode config and npm scripts
- the generic MCP runtime in `agentic-tools-mcp`

The platform tool logic now lives in a separate sibling monorepo.

## Runtime repo contents

- `/Users/maximilian/coding/opencode`
- `/Users/maximilian/coding/opencode/agentic-tools-mcp`

## Sibling tool monorepo

- `/Users/maximilian/coding/agentic-platform-tools`
- packages inside it:
  - `agentic-tools-core`
  - `agentic-tools-ashby`
  - `agentic-tools-gem`
  - `agentic-tools-harmonic`
  - `agentic-tools-metaview`

## What `crush.json` starts

- `agentic_tools_ashby`
- `agentic_tools_gem`
- `agentic_tools_harmonic`
- `agentic_tools_metaview`

Each MCP server runs over `stdio` from `/Users/maximilian/coding/opencode/.venv/bin/python`.

## Commands

Bootstrap or refresh the shared Python environment:

```bash
npm run mcp:bootstrap
```

Run the MCP smoke test across all 4 servers in `mock` mode:

```bash
npm run mcp:smoke
```

Run the live probe for the selected live integrations:

```bash
npm run mcp:probe-live
```

Run Crush interactively:

```bash
npm run crush
```

Run Crush non-interactively:

```bash
npm run crush:run -- "List the available recruiting tools."
```

## Current runtime mode

- Ashby: `live`
- Gem: `live`
- Harmonic: `live`
- Metaview: `mock`

Shared credentials are loaded from `/Users/maximilian/coding/agentic recruiting/.env` via `AR_SHARED_ENV_PATH`.

## Notes

- MCP tool parameters are exposed directly from each tool input schema. They are not wrapped in a top-level `payload` object.
- Gem write tools and Harmonic enrichment tools are staged through checkpoints.
- Checkpoint state persists in `/Users/maximilian/coding/opencode/agentic-tools-mcp/data`.
- Metaview stays in `mock` mode until a real `METAVIEW_API_KEY` is available.
- `crush run` still requires a configured provider. If none is configured, Crush will return `No providers configured`.
