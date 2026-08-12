"""
Extraction Response Parser.

Type:
    Domain Service

Purpose:
    Parse and validate candidate selections returned by the LLM.

Responsibilities:
    - Normalize the LLM response.
    - Parse JSON.
    - Validate candidate-selection structure.
    - Return candidate IDs and confidence.

Does NOT:
    - Call the LLM.
    - Retrieve knowledge.
    - Validate source grounding.
    - Generate source quotes.
    - Generate facts.
"""

from __future__ import annotations

import json
from typing import TypedDict


class ExtractionSelection(TypedDict):
    """Represent one candidate selection."""

    candidate_id: str
    confidence: float


class ExtractionResponseParser:
    """Parse candidate selections from an LLM response."""

    def parse(
        self,
        response: str,
    ) -> list[ExtractionSelection]:
        """Parse and validate candidate selections."""

        cleaned_response = self._clean_response(
            response
        )

        if not cleaned_response:
            return []

        try:
            data = json.loads(
                cleaned_response
            )
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        selections: list[ExtractionSelection] = []

        for item in data:
            selection = self._parse_item(
                item
            )

            if selection is None:
                return []

            selections.append(
                selection
            )

        return selections

    def _parse_item(
        self,
        item: object,
    ) -> ExtractionSelection | None:
        """Validate one candidate-selection object."""

        if not isinstance(item, dict):
            return None

        if set(item.keys()) != {
            "candidate_id",
            "confidence",
        }:
            return None

        candidate_id = item.get(
            "candidate_id"
        )

        confidence = item.get(
            "confidence"
        )

        if not isinstance(
            candidate_id,
            str,
        ):
            return None

        candidate_id = candidate_id.strip()

        if not candidate_id:
            return None

        if (
            not isinstance(
                confidence,
                (int, float),
            )
            or isinstance(
                confidence,
                bool,
            )
        ):
            return None

        return {
            "candidate_id": candidate_id,
            "confidence": float(
                confidence
            ),
        }

    def _clean_response(
        self,
        response: str,
    ) -> str:
        """Remove optional Markdown code fences."""

        cleaned = response.strip()

        if not cleaned.startswith("```"):
            return cleaned

        lines = cleaned.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(
            lines
        ).strip()