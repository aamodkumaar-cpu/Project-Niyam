"""
Text Chunking Utility.

Splits PDF pages into smaller overlapping chunks suitable
for embedding generation and semantic search.
"""

import re

from backend.config.settings import CHUNK_OVERLAP, CHUNK_SIZE
from backend.ingestion.Chunk import Chunk
from backend.ingestion.Page import Page


def chunk_text(
    pages: list[Page],
    chunk_size: int,
    overlap: int
) -> list[Chunk]:
    """
    Split documents into semantically meaningful chunks.

    Strategy
    --------
    1. Normalize whitespace.
    2. Split into paragraphs.
    3. Build chunks paragraph-by-paragraph.
    4. If a paragraph is too large, split into sentences.
    5. If a sentence is still too large, perform a hard split.
    """

    chunks: list[Chunk] = []
    chunk_number = 0

    for page in pages:

        text = _normalize(page.text)

        paragraphs = _split_paragraphs(text)

        current_chunk = ""

        for paragraph in paragraphs:

            # Paragraph fits in current chunk
            if len(current_chunk) + len(paragraph) + 2 <= chunk_size:

                if current_chunk:
                    current_chunk += "\n\n"

                current_chunk += paragraph
                continue

            # Flush current chunk
            if current_chunk:

                chunks.append(
                    Chunk(
                        text=current_chunk,
                        page_number=page.page_number,
                        chunk_number=chunk_number
                    )
                )

                chunk_number += 1

                current_chunk = _tail_overlap(
                    current_chunk,
                    overlap
                )

            # Large paragraph
            if len(paragraph) > chunk_size:

                sentence_chunks = _split_large_paragraph(
                    paragraph,
                    chunk_size,
                    overlap
                )

                for sentence_chunk in sentence_chunks:

                    chunks.append(
                        Chunk(
                            text=sentence_chunk,
                            page_number=page.page_number,
                            chunk_number=chunk_number
                        )
                    )

                    chunk_number += 1

                current_chunk = ""

            else:
                current_chunk += paragraph

        if current_chunk:

            chunks.append(
                Chunk(
                    text=current_chunk,
                    page_number=page.page_number,
                    chunk_number=chunk_number
                )
            )

            chunk_number += 1

    return chunks


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _normalize(text: str) -> str:
    """Normalize whitespace."""

    text = text.replace("\r", "")

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def _split_paragraphs(
    text: str
) -> list[str]:
    """Split text into paragraphs."""

    return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


def _split_large_paragraph(
    paragraph: str,
    chunk_size: int,
    overlap: int
) -> list[str]:
    """
    Split an oversized paragraph into sentence chunks.
    """

    sentences = re.split(
        r'(?<=[.!?])\s+',
        paragraph
    )

    chunks: list[str] = []

    current = ""

    for sentence in sentences:

        if len(current) + len(sentence) + 1 <= chunk_size:

            if current:
                current += " "

            current += sentence

        else:

            if current:
                chunks.append(current)

            current = sentence

            # Very long sentence
            while len(current) > chunk_size:

                chunks.append(current[:chunk_size])

                current = current[
                    chunk_size - overlap:
                ]

    if current:
        chunks.append(current)

    return chunks


def _tail_overlap(
    text: str,
    overlap: int
) -> str:
    """Return trailing overlap text."""

    if overlap <= 0:
        return ""

    return text[-overlap:]