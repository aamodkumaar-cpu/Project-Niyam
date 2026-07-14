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

from backend.config.settings import (
    CHROMA_DB_PATH,
    VECTOR_COLLECTION
)


def _coerce_str(value: object, default: str = "") -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return default
    return str(value)


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    return default


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

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        print(type(results))
        
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
            print(metadata)
            print(type(metadata["page_number"]))
            print(type(metadata["chunk_number"]))

            document_metadata = DocumentMetadata(
                document_id=str(metadata["document_id"]),
                source= str(metadata["source"]),
                page_number=int(metadata["page_number"]),
                chunk_number=int(metadata["chunk_number"])
            )

            knowledge_node = KnowledgeNode(
                content=document,
                score=distance,
                metadata=document_metadata
            )

            knowledge_nodes.append(knowledge_node)

        # print(knowledge_nodes)
        # print(knowledge_nodes)
        return knowledge_nodes