"""
Business Profile Extractor.

Purpose:
    Extracts business profile information from a user's question.

Responsibilities:
    - Extract company size
    - Extract state

Does NOT:
    - Call the LLM
    - Determine compliance
"""

import re

from backend.compliance.BusinessProfile import BusinessProfile


class BusinessProfileExtractor:
    """Extracts business profile information."""

    def extract(
        self,
        question: str
    ) -> BusinessProfile:
        """Extract a business profile from a question."""

        company_size = self._extract_company_size(question)
        state = self._extract_state(question)

        return BusinessProfile(
            business_name="Unknown",
            industry="Unknown",
            company_size=company_size,
            state=state
        )

    def _extract_company_size(
        self,
        question: str
    ) -> int:
        """Extract company size."""

        match = re.search(r"\b(\d+)\b", question)

        if match:
            return int(match.group(1))

        return 0

    def _extract_state(
        self,
        question: str
    ) -> str:
        """Extract state."""

        states = [
            "delhi",
            "maharashtra",
            "karnataka",
            "uttar pradesh"
        ]

        question = question.lower()

        for state in states:
            if state in question:
                return state.title()

        return "Unknown"