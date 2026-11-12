import pytest

from tinyrag.models import DocumentError, Element
from tinyrag.parsing import TextBlock, classify_blocks, clean_text, join_lines, parse_pdf


def test_classify_assigns_heading_levels_by_size_rank():
    blocks = [
        TextBlock("1 Chapter", page=1, font_size=18.0),
        TextBlock("1.1 Section", page=1, font_size=13.0),
        TextBlock("Body text that is long enough to dominate the page.", page=1, font_size=10.5),
    ]

    assert [e.heading_level for e in classify_blocks(blocks)] == [1, 2, None]


def test_body_size_is_determined_by_characters_not_lines():
    # Many short 8pt lines (e.g. a table) must not win against one long paragraph.
    table_cells = [TextBlock("x", page=1, font_size=8.0) for _ in range(20)]
    paragraph = TextBlock("A long paragraph " * 10, page=1, font_size=10.0)
    heading = TextBlock("Heading", page=1, font_size=14.0)

    elements = classify_blocks([heading, *table_cells, paragraph])

    assert elements[0].heading_level == 1
    assert all(e.heading_level is None for e in elements[1:])


def test_slightly_larger_text_is_not_a_heading():
    blocks = [
        TextBlock("Body text " * 10, page=1, font_size=10.0),
        TextBlock("Almost body text", page=1, font_size=10.5),
    ]

    assert [e.heading_level for e in classify_blocks(blocks)] == [None, None]


def test_classify_empty_input():
    assert classify_blocks([]) == []


def test_clean_text_resolves_ligatures_and_whitespace():
    assert clean_text("Unternehmensproﬁl  und\n Oﬀshore") == "Unternehmensprofil und Offshore"


def test_join_lines_keeps_hyphenated_words_together():
    assert join_lines(["Die Zwei-", "Faktor-Authentifizierung", "ist Pflicht."]) == (
        "Die Zwei-Faktor-Authentifizierung ist Pflicht."
    )


def test_parse_pdf_extracts_structure_and_drops_header_and_footer(pdf_bytes):
    elements = parse_pdf(pdf_bytes)

    assert elements == [
        Element("Chapter 1", page=1, heading_level=1),
        Element("Body text of chapter 1, long enough.", page=1),
        Element("Chapter 2", page=2, heading_level=1),
        Element("Body text of chapter 2, long enough.", page=2),
    ]


def test_parse_pdf_rejects_invalid_data():
    with pytest.raises(DocumentError):
        parse_pdf(b"this is not a pdf")


def test_parse_pdf_without_text_returns_no_elements(empty_pdf_bytes):
    assert parse_pdf(empty_pdf_bytes) == []
