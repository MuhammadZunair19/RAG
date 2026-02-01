"""Extract text from PDF files."""

import io
from typing import Iterator

from PyPDF2 import PdfReader


def extract_text_from_pdf(file_content: bytes) -> list[tuple[int, str]]:
    """
    Extract text per page from PDF bytes.
    Returns list of (page_number, text) (1-based page numbers).
    """
    reader = PdfReader(io.BytesIO(file_content))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append((i + 1, text.strip()))
    return pages
