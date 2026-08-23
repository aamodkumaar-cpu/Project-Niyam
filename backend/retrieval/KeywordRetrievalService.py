"""
Keyword Retrieval Service.

Type:
    Domain Service

Purpose:
    Retrieves relevant knowledge using keyword matching.

Responsibilities:
    - Search indexed knowledge using keywords
    - Retrieve a sufficiently broad candidate set for hybrid ranking
    - Return matching KnowledgeNode objects
    - Support metadata filtering

Does NOT:
    - Generate embeddings
    - Perform semantic search
    - Merge results
    - Rank results
    - Build prompts
    - Call the LLM
"""

from chromadb.types import Where

from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.RetrievalStrategy import RetrievalStrategy
from backend.retrieval.VectorRepository import VectorRepository


class KeywordRetrievalService(RetrievalStrategy):
    """Retrieves knowledge using keyword matching."""

    _DEFAULT_TOP_K: int = 20

    vector_repository: VectorRepository

    def __init__(
        self,
        vector_repository: VectorRepository
    ) -> None:
        """Initialize the keyword retrieval service."""

        self.vector_repository = vector_repository

    def retrieve(
        self,
        question: str,
        top_k: int = _DEFAULT_TOP_K,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """Retrieve a broad keyword candidate set for hybrid ranking."""

        return self.vector_repository.keyword_search(
            question=question,
            top_k=top_k,
            where=where
        )