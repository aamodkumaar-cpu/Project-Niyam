"""
Response Builder.

Type:
    Presentation Adapter

Purpose:
    Converts business objects into presentation objects.

Responsibilities:
    - Convert ComplianceChecklist to AnswerResult

Does NOT:
    - Execute business logic
    - Call tools
    - Retrieve documents
"""

from backend.compliance.ComplianceChecklist import ComplianceChecklist
from backend.retrieval.KnowledgeSearchResult import KnowledgeSearchResult
from backend.results.AnswerResult import AnswerResult


class ResponseBuilder:
    """Builds presentation responses."""

    def build(
        self,
        result
    ) -> AnswerResult:
        """Convert a business result into an AnswerResult."""

        if isinstance(result, ComplianceChecklist):

            answer = "\n".join(
                f"✓ {item.title}\n  {item.description}"
                for item in result.items
            )
            return AnswerResult(
                answer=answer,
                sources=[]
            )
        if isinstance(result, KnowledgeSearchResult):
            return AnswerResult(
                answer=result.answer,
                sources=result.sources
            )

        raise ValueError(
            f"Unsupported response type: {type(result)}"
        )