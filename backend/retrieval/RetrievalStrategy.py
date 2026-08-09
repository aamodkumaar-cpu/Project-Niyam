"""
Retrieval Strategy.

Type:
    Strategy Interface

Purpose:
    Defines the contract implemented by every retrieval strategy.

Responsibilities:
    - Retrieve relevant KnowledgeNode objects.
    - Support optional metadata filtering.

Does NOT:
    - Merge results.
    - Build prompts.
    - Call the LLM.
"""

from abc import ABC, abstractmethod

from chromadb.types import Where

from backend.retrieval.KnowledgeNode import KnowledgeNode


class RetrievalStrategy(ABC):
    """Base interface for all retrieval strategies."""

    @abstractmethod
    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """Retrieve relevant knowledge nodes."""