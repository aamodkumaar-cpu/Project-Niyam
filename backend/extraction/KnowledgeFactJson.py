"""
Knowledge Fact JSON.

Purpose:
    Represents one atomic fact returned by the knowledge extraction LLM.

Responsibilities:
    - Store the fact's company or role.
    - Store the exact source wording for the fact.
    - Store extraction confidence.

Does NOT:
    - Store document metadata.
    - Determine source documents.
    - Determine page numbers.
    - Validate grounding.
"""

from typing import TypedDict


class KnowledgeFactJson(TypedDict):
    """Represents one atomic fact returned by the extraction LLM."""

    name: str
    source_quote: str
    confidence: float