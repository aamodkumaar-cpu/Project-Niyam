"""
Context Section.

Type:
    Domain Model

Purpose:
    Represents a logical section of retrieved knowledge.

Responsibilities:
    - Group related knowledge
    - Preserve source information
    - Produce formatted context

Does NOT:
    - Retrieve knowledge
    - Rank knowledge
    - Call the LLM
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextSection:
    """Represents one logical context section."""

    title: str
    content: str