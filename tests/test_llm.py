import json

import httpx
import pytest

from tinyrag.llm import OllamaLLM


def make_llm(handler) -> OllamaLLM:
    """An LLM whose HTTP requests go to `handler` instead of a real server."""
    client = httpx.Client(base_url="http://ollama.test", transport=httpx.MockTransport(handler))
    return OllamaLLM(client, model="test-model", context_tokens=4096)


def test_sends_system_and_user_message_with_deterministic_options():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"message": {"role": "assistant", "content": " Hi. \n"}})

    answer = make_llm(handler).generate(system="Be brief.", prompt="Hello?")

    assert answer == "Hi."
    [body] = requests
    assert body["model"] == "test-model"
    assert body["messages"] == [
        {"role": "system", "content": "Be brief."},
        {"role": "user", "content": "Hello?"},
    ]
    assert body["stream"] is False
    assert body["options"] == {"temperature": 0, "num_ctx": 4096}


def test_raises_on_server_error():
    llm = make_llm(lambda request: httpx.Response(500, json={"error": "out of memory"}))

    with pytest.raises(httpx.HTTPStatusError):
        llm.generate(system="", prompt="Hello?")
