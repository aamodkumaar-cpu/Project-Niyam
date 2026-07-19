"""
Document Service.

Coordinates document management operations.
"""

from backend.ingestion.DocumentCatalogRepository import DocumentCatalogRepository
from backend.ingestion.Document import Document
from backend.ingestion.DocumentStatistics import DocumentStatistics
from backend.retrieval.VectorRepository import VectorRepository


class DocumentService:

    def __init__(
        self,
        document_repository: DocumentCatalogRepository,
        vector_repository: VectorRepository
    ):
        """Initialize the document service."""

        self.document_repository = document_repository
        self.vector_repository = vector_repository


    def list_documents(self) -> list[Document]:
        """Return all available documents."""
        return self.document_repository.list_documents()



    def get_statistics(
        self
    ) -> DocumentStatistics:
        """Return summary statistics for the knowledge base."""

        return DocumentStatistics(
            total_documents=len(
                self.list_documents()
            ),
            total_chunks=self.vector_repository.count_chunks()
        )