"""
Structured Knowledge.

Type:
    Domain Model

Purpose:
    Represents extracted knowledge from retrieved documents.

Responsibilities:
    - Hold extracted facts

Does NOT:
    - Retrieve knowledge
    - Answer questions
"""

from dataclasses import dataclass, field

from backend.extraction.KnowledgeFact import KnowledgeFact


@dataclass(slots=True)
class StructuredKnowledge:
    """Collection of extracted knowledge."""

    facts: list[KnowledgeFact] = field(
        default_factory=list
    )