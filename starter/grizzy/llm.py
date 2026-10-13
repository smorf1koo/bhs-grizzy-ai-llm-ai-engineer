"""Model access: any OpenAI-compatible chat endpoint or an offline replay of recorded answers.

Provided ready-made so you do not have to fight with SDKs. Replace it if you prefer another client.

GRIZZY_PROVIDER=openai  - Ollama, llama.cpp server, LM Studio, cloud APIs (GRIZZY_BASE_URL etc.)
GRIZZY_PROVIDER=replay  - no network: the answer is read from <GRIZZY_REPLAY_DIR>/<key>.txt,
                          e.g. replay/R03/attempt_1.txt. Use it to run the pipeline and tests
                          without a model, or paste a prompt from runs/ into any chat UI and save
                          the answer there.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from grizzy.config import Config


class LLMError(Exception):
    """The model could not be called (network, missing replay file)."""


def chat(cfg: Config, messages: list[dict], key: str = "", temperature: float = 0.2,
         timeout: float = 300.0) -> str:
    """Send chat messages, return the answer text.

    key identifies the call for the replay provider, e.g. "R03/attempt_1".
    """
    if cfg.provider == "replay":
        return replay(cfg, key)
    if cfg.provider != "openai":
        raise LLMError(f"unknown GRIZZY_PROVIDER: {cfg.provider}")
    body = json.dumps({"model": cfg.model, "messages": messages, "temperature": temperature,
                       "max_tokens": cfg.max_tokens}).encode("utf-8")
    req = urllib.request.Request(
        cfg.base_url.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {cfg.api_key}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"]


def replay(cfg: Config, key: str) -> str:
    """Return a recorded answer from <replay_dir>/<key>.txt."""
    if not key:
        raise LLMError("replay provider needs a key, e.g. chat(cfg, messages, key='R03/attempt_1')")
    path = Path(cfg.replay_dir) / f"{key}.txt"
    if not path.is_file():
        raise LLMError(f"no recorded answer: {path}")
    return path.read_text(encoding="utf-8")
