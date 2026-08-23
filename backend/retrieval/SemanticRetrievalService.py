"""
Semantic Retrieval Service.

Purpose:
    Retrieves relevant knowledge using vector similarity search.

Responsibilities:
    - Generate query embeddings
    - Perform vector search
    - Return the most relevant Knowledge Nodes

Does NOT:
    - Perform keyword search
    - Build prompts
    - Call the LLM
    - Merge retrieval results
"""

from chromadb.types import Where

from backend.ingestion.EmbeddingService import EmbeddingService
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.RetrievalStrategy import RetrievalStrategy
from backend.retrieval.VectorRepository import VectorRepository


class  SemanticRetrievalService(RetrievalStrategy):

    embedding_service: EmbeddingService
    vector_repository: VectorRepository
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_repository: VectorRepository
    ) -> None:

        self.embedding_service = embedding_service
        self.vector_repository = vector_repository

    def retrieve(
        self,
        question: str,
        top_k: int = 10,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """Retrieve relevant knowledge using semantic search."""

        query_embedding = self.embedding_service.get_embedding(question)

        return self.vector_repository.search(
            query_embedding=query_embedding,
            top_k=top_k,
            where=where
        )