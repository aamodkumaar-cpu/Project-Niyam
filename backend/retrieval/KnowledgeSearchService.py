"""
Knowledge Search Service.

Type:
    Domain Service

Purpose:
    Executes the complete knowledge search workflow.

Responsibilities:
    - Retrieve knowledge
    - Extract structured facts
    - Generate the final answer
    - Build a KnowledgeSearchResult

Does NOT:
    - Detect intent
    - Execute tools
    - Route requests
"""

from backend.diagnostic.ExecutionDebugger import ExecutionDebugger
from backend.extraction.AnswerGenerator import AnswerGenerator
from backend.extraction.KnowledgeExtractor import KnowledgeExtractor
from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.orchestration.ExecutionContext import ExecutionContext
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KnowledgeSearchResult import KnowledgeSearchResult
from backend.retrieval.RetrievalPipeline import RetrievalPipeline


class KnowledgeSearchService:
    """Executes the complete knowledge search workflow."""

    execution_debugger: ExecutionDebugger

    retrieval_pipeline: RetrievalPipeline
    knowledge_extractor: KnowledgeExtractor
    answer_generator: AnswerGenerator

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        knowledge_extractor: KnowledgeExtractor,
        answer_generator: AnswerGenerator,
        execution_debugger: ExecutionDebugger,
    ) -> None:
        """Initialize the knowledge search service."""

        self.retrieval_pipeline = retrieval_pipeline
        self.knowledge_extractor = knowledge_extractor
        self.answer_generator = answer_generator
        self.execution_debugger = execution_debugger

    def search(
        self,
        context: ExecutionContext,
    ) -> KnowledgeSearchResult:
        """Execute retrieval, validation, and answer generation."""

        question = context.request.question

        self.execution_debugger.question(
            question
        )

        knowledge_nodes = self.retrieval_pipeline.retrieve(
            question=question,
            where=context.request.where,
        )

        self.execution_debugger.retrieval(
            question=question,
            knowledge_nodes=knowledge_nodes,
        )

        structured_knowledge = self.knowledge_extractor.extract(
            question=question,
            knowledge_nodes=knowledge_nodes,
        )

        self.execution_debugger.extraction(
            structured_knowledge
        )

        answer = self.answer_generator.generate(
            question=question,
            knowledge=structured_knowledge,
        )

        self.execution_debugger.answer(
            answer
        )

        sources = self._build_sources(
            knowledge=structured_knowledge,
        )

        return KnowledgeSearchResult(
            answer=answer,
            sources=sources,
        )

    def _build_sources(
        self,
        knowledge: StructuredKnowledge,
    ) -> list[DocumentMetadata]:
        """Build unique source metadata from validated facts."""

        sources: list[DocumentMetadata] = []

        seen: set[tuple[str, int]] = set()

        for fact in knowledge.facts:

            source_key = (
                fact.source,
                fact.page_number,
            )

            if source_key in seen:
                continue

            seen.add(
                source_key
            )

            sources.append(
                DocumentMetadata(
                    document_id="",
                    source=fact.source,
                    domain=KnowledgeDomain.GENERAL,
                    compliance_pack="",
                    page_number=fact.page_number,
                    chunk_number=0,
                )
            )

        return sources