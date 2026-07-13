"""
Text Chunking Utility.

Splits PDF pages into smaller overlapping chunks suitable
for embedding generation and semantic search.
"""

from backend.ingestion.Page import Page
from backend.ingestion.Chunk import Chunk


def chunk_text(
    pages: list[Page],
    chunk_size: int = 500
) -> list[Chunk]:

    chunks = []

    for page in pages:

        text = page.text

        for i in range(0, len(text), chunk_size):

            chunks.append(
                Chunk(
                    text=text[i:i + chunk_size],
                    page_number=page.page_number
                )
            )

    return chunks