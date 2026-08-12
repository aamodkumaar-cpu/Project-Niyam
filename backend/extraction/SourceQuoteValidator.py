"""
Source Quote Validator.

Type:
Domain Service

Purpose:
Validate that an extracted fact is explicitly present in
the retrieved source content.

Responsibilities:
- Normalize source and extracted quote formatting.
- Verify exact source-quote containment.

Does NOT:
- Interpret meaning.
- Perform semantic similarity.
- Infer facts.
- Modify source content.
- Call the LLM.
"""


class SourceQuoteValidator:
    """Validates extracted quotes against source content."""

    def is_supported(
        self,
        source_quote: str,
        source_text: str,
    ) -> bool:
        """Return whether the extracted quote exists in source text."""

        normalized_quote = self._normalize(
            source_quote
        )

        normalized_source = self._normalize(
            source_text
        )

        if not normalized_quote:
            return False

        return normalized_quote in normalized_source

    def _normalize(
        self,
        text: str,
    ) -> str:
        """Normalize formatting without changing factual content."""

        normalized = " ".join(
            text.split()
        )

        if normalized.startswith("● "):
            normalized = normalized[2:]

        if normalized.startswith("- "):
            normalized = normalized[2:]

        return normalized