"""
Extraction Question Analyzer.

Type:

    Domain Service

Purpose:

    Analyze question characteristics to determine the evidence
    required for source-grounded extraction.

Responsibilities:

    - Determine evidence requirements.
    - Detect role questions.
    - Detect relationship questions.
    - Detect exhaustive requests.
    - Detect quantitative requirements.
    - Detect temporal requirements.
    - Detect structural-value requirements.
    - Detect explicit per-heading limits.

Does NOT:

    - Retrieve knowledge.
    - Rank candidates.
    - Select candidates.
    - Call the LLM.
    - Interpret domain-specific entities.
"""

from __future__ import annotations

import re

from backend.extraction.EvidenceRequirement import EvidenceRequirement


class ExtractionQuestionAnalyzer:
    """Analyze questions to determine extraction evidence requirements."""

    _MAX_PER_HEADING_PATTERNS = (
        re.compile(
            r"\b(?:top|first|best)\s+(\d+)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bmax(?:imum)?\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bup\s+to\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",
            re.IGNORECASE,
        ),
    )

    _EXHAUSTIVE_PATTERN = re.compile(
        r"\b(?:all|each|every|list|enumerate)\b",
        re.IGNORECASE,
    )

    _QUANTITY_PATTERN = re.compile(
        r"\b(?:how\s+many|how\s+much|total|number|count|"
        r"years?|months?|percentage|percent|amount|duration)\b",
        re.IGNORECASE,
    )

    _TEMPORAL_PATTERN = re.compile(
        r"\b(?:when|date|year|month|period|duration|"
        r"start(?:ed)?|end(?:ed)?|joined|left|between|"
        r"experience|experiences)\b",
        re.IGNORECASE,
    )

    _STRUCTURAL_VALUE_PATTERN = re.compile(
        r"^\s*what\s+"
        r"(?:\w+\s+){1,3}"
        r"(?:did|does|do|is|are|was|were|has|have|had)\b",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        """Initialize the question analyzer."""

    def determine_evidence_requirement(
        self,
        question: str,
    ) -> EvidenceRequirement:
        """Determine the evidence characteristics required by a question."""

        return EvidenceRequirement(
            direct_answer_required=True,
            quantity_required=self._requires_quantity(question),
            temporal_value_required=self._requires_temporal_value(question),
            relationship_required=self.is_relationship_question(question),
            structural_value_required=self._requires_structural_value(question),
        )

    def is_role_question(
        self,
        question: str,
    ) -> bool:
        """Determine whether the question asks for a role or position."""

        normalized = question.lower()

        return any(
            phrase in normalized
            for phrase in (
                "what was the role",
                "what is the role",
                "what role",
                "which role",
                "what position",
                "which position",
            )
        ) or bool(
            re.search(
                r"\b(?:what|which)\s+was\s+"
                r"\w+(?:'s|’s)\s+"
                r"(?:role|position)\b",
                normalized,
            )
        ) or bool(
            re.search(
                r"\b(?:what|which)\s+is\s+"
                r"\w+(?:'s|’s)\s+"
                r"(?:role|position)\b",
                normalized,
            )
        )

    def is_relationship_question(
        self,
        question: str,
    ) -> bool:
        """Determine whether the question asks about a relationship."""

        normalized = question.lower()

        return any(
            phrase in normalized
            for phrase in (
                "associated with",
                "related to",
                "relationship between",
                "relation between",
                "connected to",
            )
        )

    def is_exhaustive_request(
        self,
        question: str,
    ) -> bool:
        """Determine whether the question requests exhaustive coverage."""

        return bool(
            self._EXHAUSTIVE_PATTERN.search(question)
        )

    def extract_max_per_heading(
        self,
        question: str,
    ) -> int | None:
        """Extract an optional maximum number of facts per heading."""

        for pattern in self._MAX_PER_HEADING_PATTERNS:
            match = pattern.search(question)

            if match is not None:
                return int(match.group(1))

        return None

    def _requires_quantity(
        self,
        question: str,
    ) -> bool:
        """Determine whether the question requires quantitative evidence."""

        return bool(
            self._QUANTITY_PATTERN.search(question)
        )

    def _requires_temporal_value(
        self,
        question: str,
    ) -> bool:
        """Determine whether the question requires temporal evidence."""

        return bool(
            self._TEMPORAL_PATTERN.search(question)
        )

    def _requires_structural_value(
        self,
        question: str,
    ) -> bool:
        """Determine whether the question requests a structurally represented value."""

        if self.is_role_question(question):
            return True

        return bool(
            self._STRUCTURAL_VALUE_PATTERN.match(question)
        )