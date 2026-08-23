"""
Extraction Candidate.

Type:
Domain Model

Purpose:
Represent one deterministic source fragment that the LLM may select.

Responsibilities:
- Preserve original source text.
- Preserve source metadata.
- Preserve source heading.
- Preserve structural ownership context.
- Provide a stable candidate identifier.

Does NOT:
- Interpret source text.
- Call the LLM.
- Generate or rewrite facts.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.retrieval.KnowledgeNode import KnowledgeNode


@dataclass(frozen=True, slots=True)
class ExtractionCandidate:
    """Represent one deterministic source fragment."""

    candidate_id: str
    heading: str
    structural_context: str
    source_quote: str
    node: KnowledgeNode

    @property
    def source(self) -> str:
        """Return the source document name."""

        return self.node.metadata.source

    @property
    def page_number(self) -> int:
        """Return the source page number."""

        return self.node.metadata.page_number

    @property
    def source_text(self) -> str:
        """Return the complete source text owning this candidate."""

        return self.node.content