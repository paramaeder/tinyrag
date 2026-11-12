"""The RAG use cases: ingest a PDF and answer a question about the ingested PDFs."""

from dataclasses import dataclass

from tinyrag.chunking import chunk_elements
from tinyrag.embedding import Embedder
from tinyrag.llm import LLM
from tinyrag.models import DocumentError
from tinyrag.parsing import parse_pdf
from tinyrag.store import SearchResult, VectorStore

NO_ANSWER = "Dazu finde ich in den Dokumenten keine Information."

SYSTEM_PROMPT = f"""Du beantwortest Fragen ausschließlich anhand der nummerierten Auszüge
aus Dokumenten, die dir gegeben werden.

Regeln:
- Verwende nur Informationen aus den Auszügen, niemals dein Vorwissen.
- Antworte knapp und präzise in der Sprache der Frage.
- Gib am Ende die Nummern der verwendeten Auszüge an, z. B. [1] oder [2][3].
- Enthalten die Auszüge die Antwort nicht, antworte nur mit: {NO_ANSWER}"""


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[SearchResult]


class RagService:
    def __init__(self, embedder: Embedder, store: VectorStore, llm: LLM, top_k: int) -> None:
        self._embedder = embedder
        self._store = store
        self._llm = llm
        self._top_k = top_k

    def ingest_pdf(self, filename: str, data: bytes) -> int:
        """Parse, chunk, embed and store a PDF. Returns the number of chunks."""
        chunks = chunk_elements(parse_pdf(data))
        if not chunks:
            raise DocumentError(
                "Im PDF wurde kein Text gefunden (evtl. ein gescanntes Dokument ohne Textebene?)."
            )
        vectors = self._embedder.embed([chunk.content for chunk in chunks])
        self._store.replace_source(filename, chunks, vectors)
        return len(chunks)

    def ask(self, question: str) -> Answer:
        """Retrieve the most relevant chunks and let the LLM answer from them."""
        [query_vector] = self._embedder.embed([question])
        results = self._store.search(query_vector, limit=self._top_k)
        if not results:
            return Answer(NO_ANSWER, sources=[])

        prompt = build_prompt(question, results)
        return Answer(self._llm.generate(SYSTEM_PROMPT, prompt), sources=results)


def build_prompt(question: str, results: list[SearchResult]) -> str:
    excerpts = "\n\n".join(
        f"[{number}] (Quelle: {r.source}, Seite {r.chunk.page})\n{r.chunk.content}"
        for number, r in enumerate(results, start=1)
    )
    return f"Auszüge:\n\n{excerpts}\n\nFrage: {question}"
