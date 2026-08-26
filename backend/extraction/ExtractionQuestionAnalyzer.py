"""
Extraction Question Analyzer.

Type:

    Domain Service

Purpose:

    Analyze extraction questions and identify deterministic
    candidate-selection constraints.

Responsibilities:

    - Identify role questions.
    - Identify relationship or synthesis questions.
    - Identify exhaustive requests.
    - Extract explicit maximum-per-heading constraints.

Does NOT:

    - Retrieve knowledge.
    - Build candidates.
    - Rank candidates.
    - Call the LLM.
    - Generate factual content.
"""

from __future__ import annotations

import re


class ExtractionQuestionAnalyzer:
    """Analyze deterministic constraints expressed by an extraction question."""

    def is_role_question(
        self,
        question: str,
    ) -> bool:
        """Return whether the question asks for a person's role."""

        normalized = question.lower().strip()

        role_patterns = (
            r"\bwhat\s+was\b.+\brole\b",
            r"\bwhat\s+is\b.+\brole\b",
            r"\bwhat\s+was\b.+\bposition\b",
            r"\bwhat\s+is\b.+\bposition\b",
            r"\bwhat\s+position\b",
            r"\bwhat\s+role\b",
        )

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in role_patterns
        )

    def is_relationship_question(
        self,
        question: str,
    ) -> bool:
        """Return whether the question asks for a relationship or synthesis."""

        normalized = question.lower()

        relationship_patterns = (
            r"\bhow\s+are\b.+\brelated\b",
            r"\bhow\s+are\b.+\bassociated\b",
            r"\bhow\s+does\b.+\brelate\s+to\b",
            r"\bhow\s+do\b.+\brelate\s+to\b",
            r"\bhow\s+does\b.+\baffect\b",
            r"\brelationship\s+between\b",
            r"\brelation\s+between\b",
            r"\bconnection\s+between\b",
            r"\blink\s+between\b",
            r"\bconnected\b",
        )

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in relationship_patterns
        )

    def is_exhaustive_request(
        self,
        question: str,
    ) -> bool:
        """Return whether the question requests exhaustive coverage."""

        normalized = question.lower().strip()

        if re.search(
            r"\beach\s+other\b",
            normalized,
        ):
            return False

        exhaustive_patterns = (
            r"\ball\s+(?:the\s+)?(?:items?|points?|facts?|causes?|"
            r"reasons?|ways?|types?|examples?|factors?)\b",

            r"\beach\s+(?:item|point|fact|cause|reason|way|type|example|factor)\b",

            r"\bevery\s+(?:item|point|fact|cause|reason|way|type|example|factor)\b",

            r"\bfrom\s+all\s+(?:the\s+)?(?:items?|sources?|documents?|companies?|roles?|headings?)\b",

            r"\bfrom\s+each\s+(?:item|source|document)\b",

            r"\bfrom\s+every\s+(?:item|source|document)\b",
        )

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in exhaustive_patterns
        )

    def extract_max_per_heading(
        self,
        question: str,
    ) -> int | None:
        """Extract an explicit maximum-per-heading constraint."""

        patterns = (
            r"\b(?:only|exactly)\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",

            r"\b(?:max(?:imum)?|up\s+to)\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                flags=re.IGNORECASE,
            )

            if match is None:
                continue

            maximum = int(
                match.group(1)
            )

            if maximum > 0:
                return maximum

        return None
