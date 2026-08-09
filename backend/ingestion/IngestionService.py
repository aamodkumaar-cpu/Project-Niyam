"""
Ingestion Service.

Type:
    Domain Service

Purpose:
    Orchestrates the complete document ingestion pipeline.

Responsibilities:
    - Read documents
    - Chunk documents
    - Generate embeddings
    - Store knowledge in the vector repository

Does NOT:
    - Build prompts
    - Execute retrieval
    - Call the LLM
"""

from backend.config.settings import CHUNK_OVERLAP, CHUNK_SIZE

from backend.diagnostic.ExecutionDebugger import ExecutionDebugger
from backend.ingestion.Document import Document
from backend.ingestion.EmbeddingService import EmbeddingService
from backend.ingestion.PDFReader import read_pdf
from backend.ingestion.TextChunker import chunk_text
from backend.retrieval.VectorRepository import VectorRepository


class IngestionService:
    """Coordinates the document ingestion pipeline."""

    embedding_service: EmbeddingService
    vector_repository: VectorRepository
    execution_debugger: ExecutionDebugger

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_repository: VectorRepository,
        execution_debugger: ExecutionDebugger
    ) -> None:
        """Initialize the ingestion service."""

        self.embedding_service = embedding_service
        self.vector_repository = vector_repository
        self.execution_debugger = execution_debugger


    def ingest_document(
        self,
        document: Document
    ) -> None:
        """Ingest a document into the knowledge base."""

        if self.vector_repository.document_exists(document.id):
            print(f"Skipping: {document.name} (already indexed)")
            return

        pages = read_pdf(document.path)

        chunks = chunk_text(
            pages,
            CHUNK_SIZE,
            CHUNK_OVERLAP
        )

        self.execution_debugger.chunks(
            chunks
        )

        for index, chunk in enumerate(chunks):

            embedding = self.embedding_service.get_embedding(
                chunk.text
            )

            metadata = {
                "document_id": document.id,
                "source": document.name,
                "domain": document.domain.value,
                "compliance_pack": document.compliance_pack,
                "page_number": chunk.page_number,
                "chunk_number": index
            }

            self.vector_repository.store_document(
                document_id=f"{document.id}_{index}",
                document=chunk.text,
                embedding=embedding,
                metadata=metadata
            )