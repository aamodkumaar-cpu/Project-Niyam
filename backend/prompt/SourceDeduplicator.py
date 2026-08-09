"""
Source Deduplicator.

Type:
    Presentation Service

Purpose:
    Produces a clean list of unique document sources.

Responsibilities:
    - Remove duplicate document/page references
    - Preserve retrieval order
    - Return unique source metadata

Does NOT:
    - Retrieve knowledge
    - Rank knowledge
    - Build prompts
    - Call the LLM
"""

from backend.retrieval.DocumentMetadata import DocumentMetadata


class SourceDeduplicator:
    """Removes duplicate document sources."""

    def deduplicate(
        self,
        sources: list[DocumentMetadata]
    ) -> list[DocumentMetadata]:
        """
        Return unique document sources while preserving order.
        """

        unique_sources: list[DocumentMetadata] = []

        seen: set[tuple[str, int]] = set()

        for source in sources:

            key = (
                source.source,
                source.page_number
            )

            if key in seen:
                continue

            seen.add(key)
            unique_sources.append(source)

        return unique_sources