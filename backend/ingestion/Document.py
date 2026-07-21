"""
Document domain model.
"""

from dataclasses import dataclass
from backend.ingestion.KnowledgeDomain import KnowledgeDomain


@dataclass(frozen=True)
class Document:
    id: str
    name: str
    path: str
    domain: KnowledgeDomain
    compliance_pack: str