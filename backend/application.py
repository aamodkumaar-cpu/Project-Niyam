"""
Project-Niyam Application Composition Root

Responsible for wiring all application components together.
"""
from backend.retrieval.SemanticRetrievalService import SemanticRetrievalService
from backend.retrieval.KeywordRetrievalService import KeywordRetrievalService
from backend.retrieval.ResultMerger import ResultMerger

from backend.ingestion.EmbeddingService import EmbeddingService
from backend.retrieval.VectorRepository import VectorRepository
from backend.retrieval.RetrievalService import RetrievalService
from backend.prompt.PromptBuilder import PromptBuilder
from backend.llm.OllamaService import OllamaService
from backend.diagnostic.RetrievalInspector import RetrievalInspector
from backend.diagnostic.PromptInspector import PromptInspector
from backend.results.AnswerResult import AnswerResult


class Application:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.vector_repository = VectorRepository()

        self.semantic_retrieval_service = SemanticRetrievalService(
            embedding_service=self.embedding_service,
            vector_repository=self.vector_repository
        )

        self.keyword_retrieval_service = KeywordRetrievalService(
            vector_repository=self.vector_repository
        )

        self.result_merger = ResultMerger()

        self.retrieval_service = RetrievalService(
            semantic_retrieval_service=self.semantic_retrieval_service,
            keyword_retrieval_service=self.keyword_retrieval_service,
            result_merger=self.result_merger
        )
        self.prompt_builder = PromptBuilder()
        self.ollama_service = OllamaService()



    def search(
        self,
        question: str,
        where: dict | None = None
    ) -> AnswerResult:
        """Search the knowledge base and generate an answer."""

        knowledge_nodes = self.retrieval_service.retrieve( 
            question=question,
            where=where
        )

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

        # sources = []
        # for node in knowledge_nodes:
        #     sources.append(node.metadata)
        sources = [node.metadata for node in knowledge_nodes]

        return AnswerResult(
            answer=answer,
            sources=sources
        )