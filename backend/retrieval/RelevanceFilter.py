"""
Relevance Filter.

Type:
    Domain Service

Purpose:
    Remove retrieved knowledge that is below the configured
    relevance boundary.

Responsibilities:
    - Apply a generic relevance threshold.
    - Preserve the ordering established by ranking.
    - Return only sufficiently relevant knowledge nodes.

Does NOT:
    - Understand business domains.
    - Interpret the user question.
    - Know about resumes, companies, policies, or documents.
    - Modify knowledge nodes.
    - Call the LLM.
    - Perform retrieval or ranking.
"""

from __future__ import annotations

from backend.retrieval.KnowledgeNode import KnowledgeNode


class RelevanceFilter:
    """Filters ranked knowledge using a generic relevance boundary."""

    def __init__(
        self,
        minimum_score: float,
    ) -> None:
        """Initialize the relevance filter."""

        self.minimum_score = minimum_score

    def filter(
        self,
        candidates: list[KnowledgeNode],
    ) -> list[KnowledgeNode]:
        """Return candidates whose score meets the relevance boundary."""

        return [
            candidate
            for candidate in candidates
            if self._is_relevant(candidate)
        ]

    def _is_relevant(
        self,
        candidate: KnowledgeNode,
    ) -> bool:
        """Return whether a candidate meets the relevance boundary."""

        return candidate.score >= self.minimum_score