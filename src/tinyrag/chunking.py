"""Split a document into chunks along its own structure.

Rules:
1. Every heading (of any level) starts a new section. The section is named by
   its heading path, e.g. "3 Reisen und Spesen > 3.1 Reisekosten".
2. Headings without text of their own produce no chunk - they only live on in
   the path of the sections below them.
3. A section longer than max_chars is split at paragraph boundaries; a
   paragraph itself is never cut.
"""

from dataclasses import dataclass, field

from tinyrag.models import Chunk, Element

MAX_CHUNK_CHARS = 1500
PATH_SEPARATOR = " > "


@dataclass
class _Section:
    path: str
    paragraphs: list[Element] = field(default_factory=list)


def chunk_elements(elements: list[Element], max_chars: int = MAX_CHUNK_CHARS) -> list[Chunk]:
    """Turn headings and paragraphs into chunks, one per section (or more if too long)."""
    return [
        chunk
        for section in _group_into_sections(elements)
        for chunk in _split_section(section, max_chars)
    ]


def _group_into_sections(elements: list[Element]) -> list[_Section]:
    sections: list[_Section] = []
    headings: list[str] = []  # current heading path, index 0 = level 1
    current: _Section | None = None

    for element in elements:
        if element.heading_level is not None:
            # Keep the parent headings, replace everything from this level down.
            headings = [*headings[: element.heading_level - 1], element.text]
            current = None  # a section is only created once text follows
            continue
        if current is None:
            current = _Section(PATH_SEPARATOR.join(headings))
            sections.append(current)
        current.paragraphs.append(element)

    return sections


def _split_section(section: _Section, max_chars: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    batch: list[Element] = []

    for paragraph in section.paragraphs:
        batch_length = sum(len(p.text) for p in batch)
        if batch and batch_length + len(paragraph.text) > max_chars:
            chunks.append(_make_chunk(section.path, batch))
            batch = []
        batch.append(paragraph)

    chunks.append(_make_chunk(section.path, batch))
    return chunks


def _make_chunk(path: str, paragraphs: list[Element]) -> Chunk:
    text = "\n".join(p.text for p in paragraphs)
    return Chunk(section=path, text=text, page=paragraphs[0].page)
