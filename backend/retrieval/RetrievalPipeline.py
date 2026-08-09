"""
Retrieval Pipeline.

Type:
    Domain Service

Purpose:
    Executes the complete retrieval pipeline.

Responsibilities:
    - Normalize user questions
    - Coordinate retrieval
    - Delegate retrieval to RetrievalService
    - Return retrieved knowledge nodes

Does NOT:
    - Build prompts
    - Call the LLM
    - Generate embeddings
"""

from chromadb.types import Where

from backend.retrieval.CandidateFilter import CandidateFilter
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.QuestionNormalizer import QuestionNormalizer
from backend.retrieval.RetrievalService import RetrievalService


class RetrievalPipeline:
    """Coordinates the retrieval workflow."""

    retrieval_service: RetrievalService
    question_normalizer: QuestionNormalizer
    candidate_filter: CandidateFilter

    def __init__(
        self,
        retrieval_service: RetrievalService,
        question_normalizer: QuestionNormalizer,
        candidate_filter: CandidateFilter
    ) -> None:
        """Initialize the retrieval pipeline."""

        self.retrieval_service = retrieval_service
        self.question_normalizer = question_normalizer
        self.candidate_filter = candidate_filter

    def retrieve(
        self,
        question: str,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """Retrieve relevant knowledge."""

        normalized_question = self.question_normalizer.normalize(
            question
        )

        candidates = self.retrieval_service.retrieve(
            question=normalized_question,
            where=where
        )

        return self.candidate_filter.filter(
            question=normalized_question,
            candidates=candidates
        )