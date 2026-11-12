import pytest

from tinyrag.models import DocumentError
from tinyrag.service import NO_ANSWER, SYSTEM_PROMPT


def test_ingest_returns_number_of_chunks(service, pdf_bytes):
    assert service.ingest_pdf("test.pdf", pdf_bytes) == 2


def test_ingest_rejects_pdf_without_text(service, empty_pdf_bytes):
    with pytest.raises(DocumentError, match="kein Text"):
        service.ingest_pdf("scan.pdf", empty_pdf_bytes)


def test_ask_gives_llm_the_best_matching_chunks_and_the_question(service, llm, pdf_bytes):
    service.ingest_pdf("test.pdf", pdf_bytes)

    answer = service.ask("What is in chapter 2?")

    assert answer.text == "Fake answer [1]"
    assert answer.sources[0].chunk.section == "Chapter 2"
    assert answer.sources[0].source == "test.pdf"

    [(system, prompt)] = llm.calls
    assert system == SYSTEM_PROMPT
    assert "[1] (Quelle: test.pdf, Seite 2)\nChapter 2" in prompt
    assert prompt.endswith("Frage: What is in chapter 2?")


def test_ask_without_documents_does_not_call_llm(service, llm):
    answer = service.ask("Anything?")

    assert answer.text == NO_ANSWER
    assert answer.sources == []
    assert llm.calls == []
