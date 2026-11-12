"""Data types shared between the pipeline stages."""

from dataclasses import dataclass


class DocumentError(ValueError):
    """A document that cannot be processed, e.g. not a PDF or without any text."""


@dataclass(frozen=True)
class Element:
    """A heading or paragraph of a document, in reading order.

    heading_level is 1 for top-level headings, 2 for subheadings and so on,
    and None for body text.
    """

    text: str
    page: int
    heading_level: int | None = None


@dataclass(frozen=True)
class Chunk:
    """A piece of a document that is embedded and stored as one vector."""

    section: str  # heading path, e.g. "3 Reisen und Spesen > 3.1 Reisekosten"
    text: str  # the paragraphs below the heading
    page: int  # page on which the chunk starts

    @property
    def content(self) -> str:
        """What gets embedded and shown to the LLM: heading path plus text."""
        return f"{self.section}\n\n{self.text}" if self.section else self.text
