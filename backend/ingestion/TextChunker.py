"""
Text Chunking Utility.

Splits large text into smaller overlapping chunks suitable
for embedding generation and semantic search.

Designed as a reusable utility independent of storage.
"""

def chunk_text(text, chunk_size=500):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks