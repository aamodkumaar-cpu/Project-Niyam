"""
Knowledge Search Service.

Type:
    Domain Service

Purpose:
    Executes the complete knowledge search workflow.

Responsibilities:
    - Retrieve relevant knowledge
    - Build prompts
    - Call the LLM
    - Build an AnswerResult

Does NOT:
    - Route requests
    - Detect intent
    - Execute tools
"""

from backend.diagnostic.PromptInspector import PromptInspector
from backend.diagnostic.RetrievalInspector import RetrievalInspector
from backend.ingestion.EmbeddingService import EmbeddingService
from backend.llm.OllamaService import OllamaService
from backend.orchestration.RequestContext import RequestContext
from backend.prompt.PromptBuilder import PromptBuilder
from backend.retrieval.KeywordRetrievalService import KeywordRetrievalService
from backend.retrieval.ResultMerger import ResultMerger
from backend.retrieval.RetrievalService import RetrievalService
from backend.retrieval.SemanticRetrievalService import SemanticRetrievalService
from backend.retrieval.VectorRepository import VectorRepository
from backend.retrieval.KnowledgeSearchResult import KnowledgeSearchResult


class KnowledgeSearchService:
    """Performs the complete RAG workflow."""

    def __init__(self):

        embedding_service = EmbeddingService()
        vector_repository = VectorRepository()

        semantic_retrieval_service = SemanticRetrievalService(
            embedding_service=embedding_service,
            vector_repository=vector_repository
        )

        keyword_retrieval_service = KeywordRetrievalService(
            vector_repository=vector_repository
        )

        result_merger = ResultMerger()

        self.retrieval_service = RetrievalService(
            semantic_retrieval_service=semantic_retrieval_service,
            keyword_retrieval_service=keyword_retrieval_service,
            result_merger=result_merger
        )

        self.prompt_builder = PromptBuilder()
        self.ollama_service = OllamaService()

    def search(
        self,
        context: RequestContext
    ) -> KnowledgeSearchResult:
        """Execute knowledge search."""

        knowledge_nodes = self.retrieval_service.retrieve(
            question=context.question,
            where=context.where
        )

        RetrievalInspector.inspect(
            context.question,
            knowledge_nodes
        )

        messages = self.prompt_builder.build(
            question=context.question,
            knowledge_nodes=knowledge_nodes
        )

        PromptInspector.inspect(messages)

        answer = self.ollama_service.generate(
            messages
        )

        sources = [
            node.metadata
            for node in knowledge_nodes
        ]

        return KnowledgeSearchResult(
            answer=answer,
            sources=sources
        )