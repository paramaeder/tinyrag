"""Generate answers with a large language model."""

from typing import Protocol

import httpx


class LLM(Protocol):
    """Anything that can answer a prompt, guided by a system instruction."""

    def generate(self, system: str, prompt: str) -> str: ...


class OllamaLLM:
    """LLM backed by an Ollama server's /api/chat endpoint."""

    def __init__(self, client: httpx.Client, model: str, context_tokens: int) -> None:
        self._client = client
        self._model = model
        self._context_tokens = context_tokens

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
                "options": {
                    "temperature": 0,  # deterministic: same question, same answer
                    # Ollama silently cuts off the start of longer prompts - set it explicitly.
                    "num_ctx": self._context_tokens,
                },
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
