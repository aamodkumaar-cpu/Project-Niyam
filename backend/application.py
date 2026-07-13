"""
Project-Niyam Application Composition Root

Responsible for wiring all application components together.
"""

#from utils.vector_db import VectorDB
from backend.ingestion.EmbeddingService import EmbeddingService
from backend.retrieval.VectorRepository import VectorRepository
from backend.retrieval.RetrievalService import RetrievalService


class Application:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.vector_repository = VectorRepository()

        self.retrieval_service = RetrievalService(
            self.embedding_service,
            self.vector_repository
        )