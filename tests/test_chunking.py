from tinyrag.chunking import chunk_elements
from tinyrag.models import Chunk, Element


def heading(text: str, level: int, page: int = 1) -> Element:
    return Element(text, page, heading_level=level)


def paragraph(text: str, page: int = 1) -> Element:
    return Element(text, page)


def test_one_chunk_per_section_with_heading_path():
    elements = [
        heading("3 Reisen", level=1),
        heading("3.1 Reisekosten", level=2),
        paragraph("Bahn 2. Klasse."),
        paragraph("Hotel max. 140 Euro."),
        heading("3.2 Offshore", level=2),
        paragraph("Zulage 85 Euro."),
        heading("5 Ansprechpartner", level=1),
        paragraph("Personal: Miriam Okafor."),
    ]

    assert chunk_elements(elements) == [
        Chunk("3 Reisen > 3.1 Reisekosten", "Bahn 2. Klasse.\nHotel max. 140 Euro.", page=1),
        Chunk("3 Reisen > 3.2 Offshore", "Zulage 85 Euro.", page=1),
        Chunk("5 Ansprechpartner", "Personal: Miriam Okafor.", page=1),
    ]


def test_heading_without_text_produces_no_chunk():
    elements = [heading("1 Empty chapter", level=1), heading("2 Next chapter", level=1)]

    assert chunk_elements(elements) == []


def test_chunk_page_is_where_its_text_starts():
    # Heading at the bottom of page 1, its text on page 2.
    elements = [heading("3 Reisen", level=1, page=1), paragraph("Text.", page=2)]

    assert chunk_elements(elements)[0].page == 2


def test_long_section_is_split_at_paragraph_boundaries():
    elements = [
        heading("Art. 1", level=1),
        paragraph("a" * 40, page=1),
        paragraph("b" * 40, page=1),
        paragraph("c" * 40, page=2),
    ]

    chunks = chunk_elements(elements, max_chars=100)

    assert [c.text for c in chunks] == ["a" * 40 + "\n" + "b" * 40, "c" * 40]
    assert [c.page for c in chunks] == [1, 2]
    assert all(c.section == "Art. 1" for c in chunks)


def test_oversized_paragraph_is_kept_whole():
    elements = [heading("Art. 1", level=1), paragraph("x" * 200)]

    assert [c.text for c in chunk_elements(elements, max_chars=100)] == ["x" * 200]


def test_text_before_first_heading_gets_empty_section():
    chunks = chunk_elements([paragraph("Preamble.")])

    assert chunks == [Chunk("", "Preamble.", page=1)]
    assert chunks[0].content == "Preamble."


def test_content_prefixes_text_with_section_path():
    chunk = Chunk("3 Reisen > 3.1 Reisekosten", "Hotel max. 140 Euro.", page=2)

    assert chunk.content == "3 Reisen > 3.1 Reisekosten\n\nHotel max. 140 Euro."
