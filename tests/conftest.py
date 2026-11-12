"""Shared test fixtures and fakes. pytest loads this file automatically."""

import pymupdf
import pytest
from qdrant_client import QdrantClient

from tinyrag.service import RagService
from tinyrag.store import VectorStore


class FakeEmbedder:
    """Deterministic 'embedding': which of a few keywords occur in the text."""

    KEYWORDS = ("chapter 1", "chapter 2", "hotel")

    def embed(self, texts: list[str]) -> list[list[float]]:
        # The constant last dimension avoids all-zero vectors (no cosine similarity).
        return [[float(k in t.lower()) for k in self.KEYWORDS] + [0.1] for t in texts]


class FakeLLM:
    """Records every call and returns a fixed answer."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate(self, system: str, prompt: str) -> str:
        self.calls.append((system, prompt))
        return "Fake answer [1]"


@pytest.fixture
def pdf_bytes() -> bytes:
    """A two-page PDF with a running header, a footer and one chapter per page."""
    doc = pymupdf.open()
    for number in (1, 2):
        page = doc.new_page()  # 842 points high
        page.insert_text((72, 30), "Running header", fontsize=8)
        page.insert_text((72, 100), f"Chapter {number}", fontsize=16)
        page.insert_text((72, 140), f"Body text of chapter {number}, long enough.", fontsize=10)
        page.insert_text((72, page.rect.height - 20), f"Page {number}", fontsize=8)
    return doc.tobytes()


@pytest.fixture
def empty_pdf_bytes() -> bytes:
    """A valid PDF without any text, like a scan without a text layer."""
    doc = pymupdf.open()
    doc.new_page()
    return doc.tobytes()


@pytest.fixture
def llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def service(llm: FakeLLM) -> RagService:
    store = VectorStore(QdrantClient(":memory:"), collection="test")
    return RagService(FakeEmbedder(), store, llm, top_k=5)
