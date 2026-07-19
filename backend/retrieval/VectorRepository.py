"""
Vector Repository.

Purpose:
    Provides all persistence operations for the vector database.

Responsibilities:
    - Store document embeddings
    - Perform semantic similarity search
    - Map database records to KnowledgeNode objects

Does NOT:
    - Generate embeddings
    - Read PDF files
    - Build prompts
"""


import chromadb
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.DocumentMetadata import DocumentMetadata
from collections.abc import Mapping
from typing import Any

from backend.config.settings import (
    CHROMA_DB_PATH,
    VECTOR_COLLECTION
)

#Utility Method ----------------- START
def _coerce_str(
        value: object,
        default: str = ""
    ) -> str:

        if isinstance(value, str):
            return value

        if value is None:
            return default

        return str(value)

def _coerce_int(
    value: object,
    default: int = 0) -> int:

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        return int(value)

    return default

#Utility Method ------------------ END

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
        metadata):

        self.collection.add(
            ids=[document_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def _to_knowledge_node(
        self,
        document: str,
        metadata: Mapping[str,Any],
        score: float) -> KnowledgeNode:

        document_metadata = DocumentMetadata(
            document_id=_coerce_str(metadata.get("document_id")),
            source=_coerce_str(metadata.get("source")),
            page_number=_coerce_int(metadata.get("page_number")),
            chunk_number=_coerce_int(metadata.get("chunk_number"))
        )

        return KnowledgeNode(
            content=document,
            score=score,
            metadata=document_metadata
        )


    def search(
        self,
        query_embedding,
        top_k=5,
        where: dict | None = None):

        

        query = {
            "query_embeddings": [query_embedding],
            "n_results": top_k
        }
        if where:
            query["where"] = where

        results = self.collection.query(**query)
        # results = self.collection.query(
        #     query_embeddings=[query_embedding],
        #     n_results=top_k
        # )

        documents = results.get("documents")
        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if not documents or not metadatas or not distances:
            return []

        knowledge_nodes = []

        for document, metadata, distance in zip(
            documents[0],
            metadatas[0],
            distances[0]
        ):
            # print(metadata)
            # print(type(metadata["page_number"]))
            # print(type(metadata["chunk_number"]))

            knowledge_nodes.append(
                self._to_knowledge_node(
                    document=document,
                    metadata=metadata,
                    score=distance
                )
            )

        # print(knowledge_nodes)
        # print(knowledge_nodes)
        return knowledge_nodes


    def get_all_chunks(
        self) -> list[KnowledgeNode]:

        results = self.collection.get(
            include=[
                "documents",
                "metadatas"
            ]
        )

        documents = results.get("documents")
        metadatas = results.get("metadatas")

        if not documents or not metadatas:
            return []

        knowledge_nodes = []

        for document, metadata in zip(
            documents,
            metadatas
        ):

            knowledge_nodes.append(
                self._to_knowledge_node(
                    document=document,
                    metadata=metadata,
                    score=0.0
                )
            )

        return knowledge_nodes


    def document_exists(
        self,
        document_id: str ) -> bool:

        """Return True if the document has already been indexed."""

        results = self.collection.get(
            where={"document_id": document_id},
            limit=1
        )

        return len(results["ids"]) > 0


    def delete_document(
        self,
        document_id: str
    ) -> None:
        """Delete all chunks belonging to a document."""

        self.collection.delete(
            where={
                "document_id": document_id
            }
        )



    def count_chunks(
        self
    ) -> int:
        """Return the total number of indexed chunks."""
        return self.collection.count()