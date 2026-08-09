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
from backend.orchestration.ExecutionContext import ExecutionContext
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

        self.retrieval_pipeline = retrieval_pipeline
        self.knowledge_extractor = knowledge_extractor
        self.answer_generator = answer_generator
        self.execution_debugger = execution_debugger



#------------ END of init() ----------------

    def search(
        self,
        context: ExecutionContext
    ) -> KnowledgeSearchResult:

        question = context.request.question

        self.execution_debugger.question(
            question
        )

        knowledge_nodes = self.retrieval_pipeline.retrieve(
            question=question,
            where=context.request.where
        )

        self.execution_debugger.retrieval(
            question=question,
            knowledge_nodes=knowledge_nodes
        )

        structured_knowledge = self.knowledge_extractor.extract(
            question=question,
            knowledge_nodes=knowledge_nodes
        )

        self.execution_debugger.extraction(
            structured_knowledge
        )

        answer = self.answer_generator.generate(
            question=question,
            knowledge=structured_knowledge
        )

        self.execution_debugger.answer(
            answer
        )

        return KnowledgeSearchResult(
            answer=answer,
            sources=[
                node.metadata
                for node in knowledge_nodes
            ]
        )