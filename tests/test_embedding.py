import json

import httpx
import pytest

from tinyrag.embedding import BATCH_SIZE, OllamaEmbedder


def make_embedder(handler) -> OllamaEmbedder:
    """An embedder whose HTTP requests go to `handler` instead of a real server."""
    client = httpx.Client(base_url="http://ollama.test", transport=httpx.MockTransport(handler))
    return OllamaEmbedder(client, model="test-model")


def test_embeds_in_batches_and_keeps_order():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        requests.append(body)
        # Fake vector: the length of each text, so we can check the order.
        return httpx.Response(200, json={"embeddings": [[float(len(t))] for t in body["input"]]})

    texts = ["x" * n for n in range(1, BATCH_SIZE + 6)]

    vectors = make_embedder(handler).embed(texts)

    assert vectors == [[float(n)] for n in range(1, BATCH_SIZE + 6)]
    assert [len(r["input"]) for r in requests] == [BATCH_SIZE, 5]
    assert all(r["model"] == "test-model" for r in requests)


def test_raises_on_server_error():
    embedder = make_embedder(lambda request: httpx.Response(404, json={"error": "model not found"}))

    with pytest.raises(httpx.HTTPStatusError):
        embedder.embed(["text"])
