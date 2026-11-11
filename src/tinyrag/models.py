"""Data types shared between the pipeline stages."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Element:
    """A heading or paragraph of a document, in reading order.

    heading_level is 1 for top-level headings, 2 for subheadings and so on,
    and None for body text.
    """

    text: str
    page: int
    heading_level: int | None = None
