"""
Knowledge Search Result.

Type:
    Domain Model (DTO)

Purpose:
    Represents the result of a knowledge search.

Responsibilities:
    - Store the generated answer
    - Store supporting sources

Does NOT:
    - Render output
    - Execute retrieval
    - Call the LLM
"""

from dataclasses import dataclass
from backend.retrieval.DocumentMetadata import DocumentMetadata


@dataclass
class KnowledgeSearchResult:
    """Represents a knowledge search result."""

    answer: str
    sources: list[DocumentMetadata]