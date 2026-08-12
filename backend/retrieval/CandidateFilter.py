"""
Candidate Filter.

Type:
    Domain Service

Purpose:
    Remove retrieval results that have no meaningful retrieval signal.

Responsibilities:
    - Reject candidates with no retrieval relevance.
    - Preserve positively scored candidates.
    - Provide a generic retrieval-quality boundary.

Does NOT:
    - Recognize document types.
    - Recognize customers or companies.
    - Inspect document names.
    - Apply domain-specific keywords.
    - Call the LLM.
"""

from backend.retrieval.KnowledgeNode import KnowledgeNode


class CandidateFilter:
    """Filters retrieval candidates using retrieval score only."""

    def filter(
        self,
        question: str,
        candidates: list[KnowledgeNode],
    ) -> list[KnowledgeNode]:
        """Return candidates with a meaningful retrieval signal."""

        _ = question

        if not candidates:
            return []

        relevant = [
            candidate
            for candidate in candidates
            if self._has_retrieval_signal(candidate)
        ]

        return relevant if relevant else candidates

    def _has_retrieval_signal(
        self,
        candidate: KnowledgeNode,
    ) -> bool:
        """Return whether the candidate has a positive retrieval score."""

        return candidate.score > 0.0