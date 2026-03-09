from __future__ import annotations

import os
from pathlib import Path


DEFAULT_ENV_CANDIDATES = [
    Path("/Users/maximilian/coding/agentic recruiting/.env"),
    Path.cwd() / ".env",
]


def load_shared_env() -> Path | None:
    candidates: list[Path] = []
    configured = os.getenv("AR_SHARED_ENV_PATH", "").strip()
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend(DEFAULT_ENV_CANDIDATES)

    for candidate in candidates:
        if not candidate.exists():
            continue
        _load_env_file(candidate)
        return candidate
    return None


def _load_env_file(path: Path) -> None:
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
