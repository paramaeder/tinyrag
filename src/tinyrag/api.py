"""HTTP API: a thin layer that translates between HTTP and the RagService.

Run with:  uv run uvicorn tinyrag.api:app --reload
Docs at:   http://127.0.0.1:8000/docs
"""

from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

from tinyrag.config import Settings
from tinyrag.embedding import OllamaEmbedder
from tinyrag.llm import OllamaLLM
from tinyrag.models import DocumentError
from tinyrag.service import RagService
from tinyrag.store import VectorStore

app = FastAPI(title="tinyrag", description="Ask questions about your PDFs.")


@lru_cache
def get_service() -> RagService:
    """Wire up the real dependencies once (replaced by fakes in tests)."""
    settings = Settings()
    ollama = httpx.Client(base_url=settings.ollama_url, timeout=300)
    return RagService(
        embedder=OllamaEmbedder(ollama, settings.embedding_model),
        store=VectorStore(QdrantClient(path=str(settings.qdrant_path)), settings.collection_name),
        llm=OllamaLLM(ollama, settings.llm_model),
        top_k=settings.top_k,
    )


Service = Annotated[RagService, Depends(get_service)]


class DocumentResponse(BaseModel):
    filename: str
    chunks: int


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class SourceResponse(BaseModel):
    source: str
    page: int
    section: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


@app.post("/documents", status_code=201)
def upload_document(file: UploadFile, service: Service) -> DocumentResponse:
    """Upload a PDF; it is parsed, chunked, embedded and stored."""
    filename = file.filename or "upload.pdf"
    try:
        chunks = service.ingest_pdf(filename, file.file.read())
    except DocumentError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return DocumentResponse(filename=filename, chunks=chunks)


@app.post("/ask")
def ask(request: AskRequest, service: Service) -> AskResponse:
    """Answer a question using the uploaded documents."""
    answer = service.ask(request.question)
    return AskResponse(
        answer=answer.text,
        sources=[
            SourceResponse(
                source=r.source, page=r.chunk.page, section=r.chunk.section, score=r.score
            )
            for r in answer.sources
        ],
    )
