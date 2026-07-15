"""
Text Chunking Utility.

Splits PDF pages into smaller overlapping chunks suitable
for embedding generation and semantic search.
"""

from backend.ingestion.Page import Page
from backend.ingestion.Chunk import Chunk
from backend.config.settings import CHUNK_SIZE, CHUNK_OVERLAP



def chunk_text(
    pages: list[Page],
    chunk_size: int ,
    overlap: int 
) -> list[Chunk]:

    chunks = []
    chunk_number = 0


    for page in pages:

        text = page.text

        # for i in range(0, len(text), chunk_size):
        step = chunk_size - overlap
        for start in range(0, len(page.text), step):

            chunks.append(
                Chunk(
                    text=text[start:start +chunk_size],
                    page_number=page.page_number,
                    chunk_number=chunk_number
                )
            )

    return chunks