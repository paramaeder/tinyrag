"""Store chunk vectors in Qdrant and search them."""

import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient, models

from tinyrag.models import Chunk


@dataclass(frozen=True)
class SearchResult:
    """A stored chunk found by a similarity search."""

    chunk: Chunk
    source: str  # name of the document the chunk comes from
    score: float  # cosine similarity, higher is more similar


class VectorStore:
    """A Qdrant collection holding one point (vector + payload) per chunk."""

    def __init__(self, client: QdrantClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    def replace_source(self, source: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Store the chunks of a document, replacing any earlier version of it."""
        if len(chunks) != len(vectors):
            raise ValueError(f"Got {len(chunks)} chunks but {len(vectors)} vectors")
        if not chunks:
            return

        self._ensure_collection(vector_size=len(vectors[0]))
        self._client.delete(self._collection, points_selector=_source_filter(source))
        self._client.upsert(
            self._collection,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "source": source,
                        "section": chunk.section,
                        "text": chunk.text,
                        "page": chunk.page,
                    },
                )
                for chunk, vector in zip(chunks, vectors, strict=True)
            ],
        )

    def search(self, vector: list[float], limit: int) -> list[SearchResult]:
        """Return the stored chunks most similar to the given vector, best first."""
        if not self._client.collection_exists(self._collection):
            return []

        points = self._client.query_points(
            self._collection, query=vector, limit=limit, with_payload=True
        ).points
        return [
            SearchResult(
                chunk=Chunk(p.payload["section"], p.payload["text"], p.payload["page"]),
                source=p.payload["source"],
                score=p.score,
            )
            for p in points
        ]

    def _ensure_collection(self, vector_size: int) -> None:
        if not self._client.collection_exists(self._collection):
            self._client.create_collection(
                self._collection,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=models.Distance.COSINE
                ),
            )


def _source_filter(source: str) -> models.FilterSelector:
    condition = models.FieldCondition(key="source", match=models.MatchValue(value=source))
    return models.FilterSelector(filter=models.Filter(must=[condition]))
