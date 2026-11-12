import pytest
from qdrant_client import QdrantClient

from tinyrag.models import Chunk
from tinyrag.store import VectorStore

HOTEL = Chunk("3 Reisen > 3.1 Reisekosten", "Hotel max. 140 Euro.", page=2)
URLAUB = Chunk("2 Arbeitszeit > 2.2 Urlaub", "30 Urlaubstage.", page=1)


@pytest.fixture
def store() -> VectorStore:
    # A real Qdrant, but in memory: fast and nothing to clean up.
    return VectorStore(QdrantClient(":memory:"), collection="test")


def test_search_on_empty_store_returns_nothing(store):
    assert store.search([1.0, 0.0], limit=5) == []


def test_search_returns_most_similar_chunk_first(store):
    store.replace_source("handbuch.pdf", [HOTEL, URLAUB], [[1.0, 0.0], [0.0, 1.0]])

    results = store.search([0.9, 0.1], limit=5)

    assert [r.chunk for r in results] == [HOTEL, URLAUB]
    assert results[0].source == "handbuch.pdf"
    assert results[0].score > results[1].score


def test_replace_source_removes_previous_version(store):
    store.replace_source("handbuch.pdf", [HOTEL, URLAUB], [[1.0, 0.0], [0.0, 1.0]])
    store.replace_source("handbuch.pdf", [URLAUB], [[0.0, 1.0]])

    assert [r.chunk for r in store.search([1.0, 0.0], limit=5)] == [URLAUB]


def test_replace_source_keeps_other_sources(store):
    store.replace_source("a.pdf", [HOTEL], [[1.0, 0.0]])
    store.replace_source("b.pdf", [URLAUB], [[0.0, 1.0]])

    assert {r.source for r in store.search([1.0, 1.0], limit=5)} == {"a.pdf", "b.pdf"}


def test_rejects_mismatched_chunks_and_vectors(store):
    with pytest.raises(ValueError):
        store.replace_source("a.pdf", [HOTEL, URLAUB], [[1.0, 0.0]])
