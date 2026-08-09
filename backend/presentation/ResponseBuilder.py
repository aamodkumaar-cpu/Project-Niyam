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


from backend.retrieval.KnowledgeSearchResult import KnowledgeSearchResult
from backend.results.AnswerResult import AnswerResult
from backend.tools.results.ComplianceChecklistResult import ComplianceChecklistResult
from backend.tools.results.ToolResult import ToolResult


class ResponseBuilder:
    """Builds presentation responses."""

    def build(
        self,
        result: ToolResult
    ) -> AnswerResult:
        """
        Convert a ToolResult into an AnswerResult.
        """
        if isinstance(result, ComplianceChecklistResult):
            checklist = result.checklist
            return AnswerResult(
                answer="\n".join(
                    f"✓ {item.title}\n  {item.description}"
                    for item in checklist.items
                ),
                sources=[]
            )

        if isinstance(result, KnowledgeSearchResult):
            return AnswerResult(
                answer=result.answer,
                sources=result.sources
            )

        raise TypeError(
            f"Unsupported ToolResult type: {type(result).__name__}"
        )
