"""
Project-Niyam Application Composition Root

Responsible for wiring all application components together.
"""

#from utils.vector_db import VectorDB
from ipaddress import ip_address
from backend.ingestion.EmbeddingService import EmbeddingService
from backend.retrieval.VectorRepository import VectorRepository
from backend.retrieval.RetrievalService import RetrievalService
from backend.prompt.PromptBuilder import PromptBuilder
from backend.llm.OllamaService import OllamaService
from backend.diagnostic.RetrievalInspector import RetrievalInspector
from backend.diagnostic.PromptInspector import PromptInspector
from backend.result.AnswerResult import AnswerResult


class Application:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.vector_repository = VectorRepository()
        self.retrieval_service = RetrievalService(
            self.embedding_service,
            self.vector_repository
        )
        self.prompt_builder = PromptBuilder()
        self.ollama_service = OllamaService()



    def search( self, question: str) -> AnswerResult:

        knowledge_nodes = self.retrieval_service.retrieve(question)

        RetrievalInspector.inspect(
            question,
            knowledge_nodes
        )

        messages = self.prompt_builder.build(
            question=question,
            knowledge_nodes=knowledge_nodes
        )
        PromptInspector.inspect(messages)
        answer = self.ollama_service.generate(messages)

        sources = []

        for node in knowledge_nodes:
            sources.append(node.metadata)

        return AnswerResult(
            answer=answer,
            sources=sources
        )