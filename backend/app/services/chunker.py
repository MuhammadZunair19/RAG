"""Split text into semantic chunks for RAG."""

from langchain.text_splitter import RecursiveCharacterTextSplitter


# ~500-1000 tokens ≈ ~2000-4000 chars (rough)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_text_splitter(
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def chunk_pages(
    pages: list[tuple[int, str]],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[tuple[str, int | None]]:
    """
    Split page texts into chunks. Returns list of (chunk_text, page_number).
    page_number is None when chunk spans multiple pages (we use first page).
    """
    splitter = get_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    result: list[tuple[str, int | None]] = []
    for page_num, text in pages:
        if not text:
            continue
        for chunk in splitter.split_text(text):
            result.append((chunk, page_num))
    return result
