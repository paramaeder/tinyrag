import pytest
from fastapi.testclient import TestClient

from tinyrag.api import app, get_service


@pytest.fixture
def client(service):
    # Swap the real service (Ollama, Qdrant on disk) for the one built from fakes.
    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def upload(client, content: bytes, filename: str = "test.pdf"):
    return client.post("/documents", files={"file": (filename, content, "application/pdf")})


def test_upload_document(client, pdf_bytes):
    response = upload(client, pdf_bytes)

    assert response.status_code == 201
    assert response.json() == {"filename": "test.pdf", "chunks": 2}


def test_upload_invalid_file_returns_422(client):
    response = upload(client, b"not a pdf", filename="fake.pdf")

    assert response.status_code == 422
    assert "kein gültiges PDF" in response.json()["detail"]


def test_upload_pdf_without_text_returns_422(client, empty_pdf_bytes):
    response = upload(client, empty_pdf_bytes, filename="scan.pdf")

    assert response.status_code == 422
    assert "kein Text" in response.json()["detail"]


def test_ask_returns_answer_with_sources(client, pdf_bytes):
    upload(client, pdf_bytes)

    response = client.post("/ask", json={"question": "What is in chapter 1?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Fake answer [1]"
    best = body["sources"][0]
    assert (best["source"], best["page"], best["section"]) == ("test.pdf", 1, "Chapter 1")
    assert best["score"] > 0  # no upper bound: float rounding can yield 1.0000001


def test_ask_rejects_too_short_question(client):
    assert client.post("/ask", json={"question": "?"}).status_code == 422
