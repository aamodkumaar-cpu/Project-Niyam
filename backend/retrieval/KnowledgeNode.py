"""
Knowledge Node.

Type:
    Domain Model

Purpose:
    Represents one retrieved knowledge chunk together with its retrieval metadata.

Responsibilities:
    - Store chunk content.
    - Store retrieval score.
    - Store document metadata.

Does NOT:
    - Perform retrieval.
    - Rank results.
    - Build prompts.
    - Call the LLM.
"""

from dataclasses import dataclass

from backend.retrieval.DocumentMetadata import DocumentMetadata


@dataclass(slots=True)
class KnowledgeNode:
    """Represents a retrieved knowledge chunk."""

    content: str
    score: float
    metadata: DocumentMetadata