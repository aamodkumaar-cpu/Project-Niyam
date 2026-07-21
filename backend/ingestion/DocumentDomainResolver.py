"""
Document Domain Resolver.

Purpose:
    Determines the knowledge domain of a document.

Responsibilities:
    - Resolve document domain
    - Apply domain classification rules

Does NOT:
    - Read PDF content
    - Store documents
    - Perform retrieval
"""

from pathlib import Path

from backend.ingestion.KnowledgeDomain import KnowledgeDomain


class DocumentDomainResolver:
    """Resolves the knowledge domain for a document."""

    @staticmethod
    def resolve(
        document_name: str
    ) -> KnowledgeDomain:
        """Return the knowledge domain for a document."""

        name = Path(document_name).stem.upper()

        if "GST" in name:
            return KnowledgeDomain.GST

        if "PF" in name:
            return KnowledgeDomain.PF

        if "ESIC" in name:
            return KnowledgeDomain.ESIC

        if "LABOUR" in name:
            return KnowledgeDomain.LABOUR

        if "MCA" in name:
            return KnowledgeDomain.MCA

        if "TDS" in name:
            return KnowledgeDomain.TDS

        if "MSME" in name:
            return KnowledgeDomain.MSME

        if "INCOME" in name:
            return KnowledgeDomain.INCOME_TAX

        return KnowledgeDomain.GENERAL