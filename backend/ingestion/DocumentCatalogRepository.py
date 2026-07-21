"""
Document Repository.

Purpose:
    Provides access to documents available for ingestion.

Responsibilities:
    - Discover available PDF documents
    - Build Document domain objects
    - Return available documents

Does NOT:
    - Read PDF contents
    - Generate embeddings
    - Ingest documents
    - Store vectors
"""


from pathlib import Path
from backend.ingestion.Document import Document
from backend.ingestion.DocumentDomainResolver import DocumentDomainResolver


class DocumentCatalogRepository:

    def __init__(
        self,
        documents_directory: Path
    ):
        self.documents_directory = documents_directory

    def list_documents(self) -> list[Document]:
        """Return all available documents."""

        documents = []

        for path in sorted(self.documents_directory.rglob("*.pdf")):

            documents.append(
                Document(
                    id=path.stem,
                    name=path.name,
                    path=str(path),
                    domain=DocumentDomainResolver.resolve(path.name),
                    compliance_pack = path.parent.name
                )
            )

        return documents