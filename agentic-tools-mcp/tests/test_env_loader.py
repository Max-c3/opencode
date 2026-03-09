from __future__ import annotations

from pathlib import Path

from agentic_tools_mcp.env_loader import load_shared_env


def test_load_shared_env_respects_configured_path(monkeypatch, tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("AR_INTEGRATION_MODE=live\nASHBY_API_KEY=test-key\n")
    monkeypatch.setenv("AR_SHARED_ENV_PATH", str(env_path))
    monkeypatch.delenv("ASHBY_API_KEY", raising=False)

    loaded = load_shared_env()

    assert loaded == env_path
    assert "ASHBY_API_KEY" in __import__("os").environ
