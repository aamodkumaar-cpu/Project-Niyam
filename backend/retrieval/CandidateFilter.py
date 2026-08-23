"""
Candidate Filter.

Type:
    Domain Service

Purpose:
    Remove retrieval candidates that are not suitable for
    downstream knowledge processing.

Responsibilities:
    - Reject candidates with no retrieval relevance.
    - Reject question and activity chunks.
    - Preserve valid positively scored candidates.
    - Provide a generic candidate-quality boundary.

Does NOT:
    - Recognize document types.
    - Recognize customers or companies.
    - Inspect document names.
    - Apply domain-specific keywords.
    - Call the LLM.
"""

import re

from backend.retrieval.KnowledgeNode import KnowledgeNode


class CandidateFilter:
    """Filters retrieval candidates using generic eligibility rules."""

    def filter(
        self,
        question: str,
        candidates: list[KnowledgeNode],
    ) -> list[KnowledgeNode]:
        """Return candidates suitable for downstream processing."""

        _ = question

        if not candidates:
            return []

        return [
            candidate
            for candidate in candidates
            if self._has_retrieval_signal(candidate)
            and self._is_knowledge_candidate(candidate.content)
        ]

    def _has_retrieval_signal(
        self,
        candidate: KnowledgeNode,
    ) -> bool:
        """Return whether the candidate has a positive retrieval score."""

        return candidate.score > 0.0

    def _is_knowledge_candidate(
        self,
        content: str,
    ) -> bool:
        """Return whether content represents knowledge rather than an activity."""

        normalized = " ".join(
            content.split()
        ).strip()

        if not normalized:
            return False

        question_count = normalized.count("?")

        numbered_question_count = len(
            re.findall(
                r"\b\d+\.\s+.*?\?",
                normalized,
            )
        )

        instruction_count = len(
            re.findall(
                r"\b(?:explain|discuss|develop|prepare|create|"
                r"document|translate|divide|identify|describe|"
                r"compare|write|list|state|observe)\b",
                normalized,
                flags=re.IGNORECASE,
            )
        )

        if numbered_question_count >= 2:
            return False

        if question_count >= 2:
            return False

        if instruction_count >= 2 and question_count >= 1:
            return False

        if question_count == 1:
            return False

        return True