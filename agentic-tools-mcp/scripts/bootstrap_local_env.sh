#!/usr/bin/env bash
set -euo pipefail

MCP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_ROOT="$(cd "$MCP_ROOT/.." && pwd)"
PLATFORM_ROOT="${PLATFORM_ROOT:-$(cd "$RUNTIME_ROOT/../agentic-platform-tools" && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-/opt/homebrew/bin/python3.11}"

"$PYTHON_BIN" -m venv "$RUNTIME_ROOT/.venv"
"$RUNTIME_ROOT/.venv/bin/pip" install --upgrade pip setuptools wheel
"$RUNTIME_ROOT/.venv/bin/pip" install "pytest>=8.3.2"
"$RUNTIME_ROOT/.venv/bin/pip" install \
  -e "$PLATFORM_ROOT/agentic-tools-core" \
  -e "$PLATFORM_ROOT/agentic-tools-ashby" \
  -e "$PLATFORM_ROOT/agentic-tools-gem" \
  -e "$PLATFORM_ROOT/agentic-tools-harmonic" \
  -e "$PLATFORM_ROOT/agentic-tools-metaview" \
  -e "$MCP_ROOT"
