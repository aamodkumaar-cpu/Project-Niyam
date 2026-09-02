"""
Evidence Signal Detector.

Type:

    Domain Service

Purpose:

    Detect generic evidence characteristics present in source text.

Responsibilities:

    - Detect quantitative evidence.
    - Detect temporal evidence.
    - Detect relationship evidence.
    - Provide deterministic evidence signals for ranking.

Does NOT:

    - Interpret domain-specific meaning.
    - Determine question relevance.
    - Rank candidates.
    - Retrieve knowledge.
    - Call the LLM.
    - Generate factual content.
"""

from __future__ import annotations

import re


class EvidenceSignalDetector:
    """Detect generic evidence characteristics in source text."""

    _QUANTITY_PATTERN = re.compile(
        r"""
        (
            \b\d+(?:\.\d+)?\s*
            (?:%|percent|million|billion|thousand|lakh|crore|
            years?|months?|days?|hours?|minutes?)
            \b
        )
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    _TEMPORAL_PATTERN = re.compile(
        r"""
        (
            \b(?:19|20)\d{2}\b
            |
            \b\d{1,2}[/-]\d{1,2}[/-](?:19|20)?\d{2,4}\b
            |
            \b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)
            [a-z]*\.?\s+(?:19|20)\d{2}\b
            |
            \b\d+\s+(?:years?|months?|weeks?|days?)\b
            |
            \b(?:since|until|from|between|during)\b
        )
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    _RELATIONSHIP_PATTERN = re.compile(
        r"""
        \b
        (?:
            related\s+to
            |associated\s+with
            |connected\s+to
            |linked\s+to
            |depends\s+on
            |integrates?\s+with
            |interacts?\s+with
            |works?\s+with
            |belongs?\s+to
            |part\s+of
            |used\s+by
            |provided\s+by
            |managed\s+by
            |owned\s+by
            |supports?\s+
            |enables?\s+
            |affects?\s+
            |influences?\s+
            |impacts?\s+
            |causes?\s+
            |prevents?\s+
            |requires?\s+
        )
        \b
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    def has_quantity(self, text: str) -> bool:
        """Return whether text contains quantitative evidence."""

        return bool(
            self._QUANTITY_PATTERN.search(text)
        )

    def has_temporal_value(self, text: str) -> bool:
        """Return whether text contains temporal evidence."""

        return bool(
            self._TEMPORAL_PATTERN.search(text)
        )

    def has_relationship(self, text: str) -> bool:
        """Return whether text contains relationship evidence."""

        return bool(
            self._RELATIONSHIP_PATTERN.search(text)
        )