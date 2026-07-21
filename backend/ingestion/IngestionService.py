
"""
Ingestion Service.

Orchestrates the complete document ingestion pipeline.

Reads a document, splits it into chunks, generates embeddings
for each chunk and stores them in the vector database.
"""

from backend.config.settings import CHUNK_OVERLAP, CHUNK_SIZE
from backend.diagnostic.ChunkInspector import ChunkInspector
from backend.ingestion.Document import Document
from backend.ingestion.EmbeddingService import EmbeddingService
from backend.retrieval.VectorRepository import VectorRepository

from backend.ingestion.PDFReader import read_pdf
from backend.ingestion.TextChunker import chunk_text


class IngestionService:

    def __init__(self):
        self.vector_repository = VectorRepository()
        self.embedding_service= EmbeddingService()



    def ingest_document(
        self,
        document:Document
    ):

        if self.vector_repository.document_exists(document.id):
            print(f"Skipping: {document.name} (already indexed)")
            return
        # Step 1 - Read PDF
        pages = read_pdf(document.path)


        # Step 2 - Split into chunks
        chunks = chunk_text( pages, CHUNK_SIZE, CHUNK_OVERLAP)
        
        ChunkInspector.inspect(chunks)
        
        # Step 3 - Process each chunk
        for index, chunk in enumerate(chunks):

            embedding = self.embedding_service.get_embedding(chunk.text)

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