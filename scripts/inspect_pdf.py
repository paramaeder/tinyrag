"""Print every text line of a PDF with its font size, bold flag and position.

A debugging aid for tuning the heading heuristic in tinyrag.parsing.

Usage:
    uv run python scripts/inspect_pdf.py path/to/file.pdf [max_pages]
"""

import sys

import pymupdf

BOLD_FLAG = 16  # bit 4 of a span's "flags" marks bold text


def main() -> None:
    path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    doc = pymupdf.open(path)
    print(f"{'page':>4} {'y':>5} {'size':>5} bold  text")
    for page in list(doc)[:max_pages]:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):  # image blocks have no "lines"
                spans = line["spans"]
                text = "".join(span["text"] for span in spans).strip()
                if not text:
                    continue
                first = spans[0]
                bold = "x" if first["flags"] & BOLD_FLAG else ""
                y = line["bbox"][1]
                size = first["size"]
                print(f"{page.number + 1:>4} {y:>5.0f} {size:>5.1f} {bold:^4}  {text[:70]}")


if __name__ == "__main__":
    main()
