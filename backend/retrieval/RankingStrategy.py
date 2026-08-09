"""
Ranking Strategy.

Type:
    Strategy Interface

Purpose:
    Defines the contract for ranking retrieved knowledge nodes.

Responsibilities:
    - Score candidate knowledge nodes.
    - Return candidates ordered by relevance.

Does NOT:
    - Retrieve documents.
    - Build prompts.
    - Call the LLM.
"""

from abc import ABC, abstractmethod

from backend.retrieval.KnowledgeNode import KnowledgeNode


class RankingStrategy(ABC):
    """Base interface for all ranking strategies."""

    @abstractmethod
    def rank(
        self,
        question: str,
        candidates: list[KnowledgeNode]
    ) -> list[KnowledgeNode]:
        """Return candidates ordered by relevance."""