"""Configuration from environment variables (optionally loaded from .env)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: Path = Path(".env")) -> None:
    """Minimal .env loader: KEY=VALUE lines, existing environment wins."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Config:
    base_url: str
    model: str
    api_key: str
    godot_bin: str
    provider: str = "openai"  # openai | replay
    replay_dir: str = "replay"
    max_tokens: int = 2048
    budget_tokens: int = 3000
    max_attempts: int = 2  # first attempt + one retry

    @staticmethod
    def from_env(**overrides) -> "Config":
        load_dotenv()
        values = dict(
            base_url=os.environ.get("GRIZZY_BASE_URL", "http://localhost:11434/v1"),
            model=os.environ.get("GRIZZY_MODEL", "qwen2.5-coder:7b"),
            api_key=os.environ.get("GRIZZY_API_KEY", "ollama"),
            godot_bin=os.environ.get("GODOT_BIN", "godot"),
            provider=os.environ.get("GRIZZY_PROVIDER", "openai"),
            replay_dir=os.environ.get("GRIZZY_REPLAY_DIR", "replay"),
            max_tokens=int(os.environ.get("GRIZZY_MAX_TOKENS", "2048")),
        )
        values.update({k: v for k, v in overrides.items() if v is not None})
        return Config(**values)
