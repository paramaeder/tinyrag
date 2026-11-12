"""Turn texts into vectors."""

from typing import Protocol

import httpx

BATCH_SIZE = 32  # texts per request, keeps single requests short


class Embedder(Protocol):
    """Anything that can turn texts into vectors (one vector per text)."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OllamaEmbedder:
    """Embedder backed by an Ollama server's /api/embed endpoint."""

    def __init__(self, client: httpx.Client, model: str) -> None:
        self._client = client
        self._model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start : start + BATCH_SIZE]
            response = self._client.post("/api/embed", json={"model": self._model, "input": batch})
            response.raise_for_status()
            vectors.extend(response.json()["embeddings"])
        return vectors
