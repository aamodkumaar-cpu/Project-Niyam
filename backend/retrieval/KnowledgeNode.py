from dataclasses import dataclass

from backend.retrieval.DocumentMetadata import DocumentMetadata


@dataclass
class KnowledgeNode:
    content: str
    score: float
    metadata: DocumentMetadata