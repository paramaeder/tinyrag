"""Generate answers with a large language model."""

from typing import Protocol

import httpx


class LLM(Protocol):
    """Anything that can answer a prompt, guided by a system instruction."""

    def generate(self, system: str, prompt: str) -> str: ...


class OllamaLLM:
    """LLM backed by an Ollama server's /api/chat endpoint."""

    def __init__(self, client: httpx.Client, model: str) -> None:
        self._client = client
        self._model = model

    def generate(self, system: str, prompt: str) -> str:
        response = self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": 0},  # deterministic: same question, same answer
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
