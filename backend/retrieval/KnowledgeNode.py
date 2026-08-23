"""
Knowledge Node.

Type:
    Domain Model

Purpose:
    Represents one retrieved knowledge chunk together with its retrieval signals.

Responsibilities:
    - Store chunk content.
    - Store semantic distance when available.
    - Store keyword relevance when available.
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
    keyword_score: float = 0.0
    semantic_distance: float | None = None