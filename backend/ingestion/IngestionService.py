
"""
Document Service.

Orchestrates the complete document ingestion pipeline.

Reads a document, splits it into chunks, generates embeddings
for each chunk and stores them in the vector database.
"""

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
        document_id,
        pdf_path
    ):

        # Step 1 - Read PDF
        pages = read_pdf(pdf_path)


        # Step 2 - Split into chunks
        chunks = chunk_text(pages)

        # Step 3 - Process each chunk
        for index, chunk in enumerate(chunks):

            embedding = self.embedding_service.get_embedding(chunk.text)

            metadata = {
                "document_id": document_id,
                "source": pdf_path.name,
                "page_number": chunk.page_number,
                "chunk_number": index
            }

            self.vector_repository.store_document(
                document_id=f"{document_id}_{index}",
                document=chunk.text,
                embedding=embedding,
                metadata=metadata
            )