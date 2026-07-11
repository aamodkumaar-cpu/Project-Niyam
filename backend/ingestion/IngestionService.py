
"""
Document Service.

Orchestrates the complete document ingestion pipeline.

Reads a document, splits it into chunks, generates embeddings
for each chunk and stores them in the vector database.
"""

from backend.ingestion.EmbeddingService import get_embedding
from backend.retrieval.VectorRepository import VectorRepository

from backend.ingestion.PDFReader import read_pdf
from backend.ingestion.TextChunker import chunk_text


class IngestionService:

    def __init__(self):

        self.vector_repository = VectorRepository()

    def ingest_document(
        self,
        document_id,
        pdf_path
    ):

        # Step 1 - Read PDF
        text = read_pdf(pdf_path)

        # Step 2 - Split into chunks
        chunks = chunk_text(text)

        # Step 3 - Process each chunk
        for index, chunk in enumerate(chunks):

            embedding = get_embedding(chunk)

            metadata = {
                "document_id": document_id,
                "chunk_number": index
            }

            self.vector_repository.store_document(
                document_id=f"{document_id}_{index}",
                document=chunk,
                embedding=embedding,
                metadata=metadata
            )