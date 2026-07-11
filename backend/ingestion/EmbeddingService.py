"""
Embedding Service.

Responsible for converting plain text into vector embeddings
using the configured embedding model.

Other components should use this service instead of calling
the embedding model directly.
"""

from ollama import embed
from backend.config.settings import EMBEDDING_MODEL



def get_embedding(text):

    response = embed(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response["embeddings"][0]