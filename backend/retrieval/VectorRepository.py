"""
Vector Repository.

Responsible for all interactions with the vector database.

Provides a clean interface for storing and retrieving document
embeddings while hiding the underlying database implementation.
"""


import chromadb

from backend.config.settings import (
    CHROMA_DB_PATH,
    VECTOR_COLLECTION
)


class VectorRepository:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=VECTOR_COLLECTION
        )

    def store_document(
        self,
        document_id,
        document,
        embedding,
        metadata
    ):

        self.collection.add(
            ids=[document_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
    )
