"""
Knowledge Search Tool.

Type:
    Tool Adapter

Purpose:
    Executes knowledge search requests.

Responsibilities:
    - Delegate knowledge search to the KnowledgeSearchService

Does NOT:
    - Retrieve vectors directly
    - Build prompts
    - Call the LLM directly
"""

from backend.orchestration.RequestContext import RequestContext
from backend.retrieval.KnowledgeSearchService import KnowledgeSearchService
from backend.retrieval.KnowledgeSearchResult import KnowledgeSearchResult
from backend.tools.Tool import Tool


class KnowledgeSearchTool(Tool):
    """Knowledge search tool."""

    def __init__(self):
        """Initialize the tool."""

        self.service = KnowledgeSearchService()

    def execute(
        self,
        context: RequestContext
    ) -> KnowledgeSearchResult:
        """Execute the tool."""

        return self.service.search(
            context
        )