"""Turn a PDF into a flat list of headings and paragraphs.

PDFs have no notion of "heading" - only text of a certain size at a certain
position. We derive the structure with two heuristics:

1. The font size covering the most characters is the body text size.
2. Every larger font size is a heading; the largest is level 1, the next level 2, ...

Text inside a band at the top and bottom of each page is treated as running
header/footer and dropped.
"""

import unicodedata
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

import pymupdf

from tinyrag.models import Element

MARGIN_BAND = 50  # PDF points at top and bottom of a page considered header/footer
MIN_HEADING_DELTA = 1.0  # a heading must be at least this much larger than body text


@dataclass(frozen=True)
class TextBlock:
    """A raw block of text as found in the PDF, before structure is derived."""

    text: str
    page: int
    font_size: float


def parse_pdf(data: bytes) -> list[Element]:
    """Parse PDF bytes into headings and paragraphs in reading order."""
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        blocks = [block for page in doc for block in extract_blocks(page)]
    return classify_blocks(blocks)


def extract_blocks(page: pymupdf.Page) -> list[TextBlock]:
    """Extract the text blocks of one page, skipping header and footer bands."""
    blocks = []
    for block in page.get_text("dict")["blocks"]:
        if "lines" not in block:  # image block
            continue
        _, top, _, bottom = block["bbox"]
        if bottom < MARGIN_BAND or top > page.rect.height - MARGIN_BAND:
            continue

        lines = ["".join(span["text"] for span in line["spans"]) for line in block["lines"]]
        text = clean_text(join_lines(lines))
        if text:
            spans = [span for line in block["lines"] for span in line["spans"]]
            font_size = _most_common_size((round(s["size"], 1), s["text"]) for s in spans)
            blocks.append(TextBlock(text, page.number + 1, font_size))
    return blocks


def classify_blocks(blocks: list[TextBlock]) -> list[Element]:
    """Decide for each block whether it is body text or a heading of some level."""
    if not blocks:
        return []

    body_size = _most_common_size((b.font_size, b.text) for b in blocks)
    heading_sizes = sorted(
        {b.font_size for b in blocks if b.font_size >= body_size + MIN_HEADING_DELTA},
        reverse=True,
    )
    level_by_size = {size: level for level, size in enumerate(heading_sizes, start=1)}
    return [Element(b.text, b.page, level_by_size.get(b.font_size)) for b in blocks]


def join_lines(lines: list[str]) -> str:
    """Join the lines of a block. A line ending in '-' continues without a space."""
    text = ""
    for line in lines:
        line = line.strip()
        separator = "" if not text or text.endswith("-") else " "
        text += separator + line
    return text


def clean_text(text: str) -> str:
    """Normalize Unicode (e.g. the ligature 'ﬁ' -> 'fi') and collapse whitespace."""
    return " ".join(unicodedata.normalize("NFKC", text).split())


def _most_common_size(sized_texts: Iterable[tuple[float, str]]) -> float:
    """The font size that covers the most characters (not the most lines)."""
    chars_per_size = Counter()
    for size, text in sized_texts:
        chars_per_size[size] += len(text)
    return chars_per_size.most_common(1)[0][0]
