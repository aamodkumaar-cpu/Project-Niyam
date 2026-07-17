"""
Document Service.

Coordinates document management operations.
"""

from backend.ingestion.DocumentCatalogRepository import DocumentCatalogRepository
from backend.ingestion.Document import Document


class DocumentService:

    def __init__(
        self,
        document_repository: DocumentCatalogRepository
    ):
        self.document_repository = document_repository

    def list_documents(self) -> list[Document]:
        """Return all available documents."""

        return self.document_repository.list_documents()
