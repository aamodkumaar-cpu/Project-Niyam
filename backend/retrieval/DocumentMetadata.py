"""
Document Metadata.

Purpose:
    Represents metadata associated with a retrieved knowledge chunk.

Responsibilities:
    - Store document identity
    - Store document source
    - Store document location within the document
    - Store document domain
    - Store compliance pack

Does NOT:
    - Read documents
    - Perform retrieval
    - Modify metadata
"""

from dataclasses import dataclass
from backend.ingestion.KnowledgeDomain import KnowledgeDomain


@dataclass
class DocumentMetadata:
    """Represents metadata for a retrieved knowledge chunk."""

    document_id: str
    source: str
    domain: KnowledgeDomain
    compliance_pack: str
    page_number: int
    chunk_number: int
    
