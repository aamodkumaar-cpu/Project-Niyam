"""
Knowledge Fact.

Type:
    Domain Model

Purpose:
    Represents one atomic fact extracted from a document.

Responsibilities:
    - Store one extracted fact
    - Preserve source metadata

Does NOT:
    - Interpret facts
    - Retrieve knowledge
    - Answer questions
"""

from dataclasses import dataclass


@dataclass(slots=True)
class KnowledgeFact:
    """Represents one extracted fact."""

    name: str

    value: str

    source: str

    page_number: int

    confidence: float