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

from backend.orchestration.ExecutionContext import ExecutionContext
from backend.orchestration.RequestContext import RequestContext
from backend.retrieval.KnowledgeSearchService import KnowledgeSearchService
from backend.retrieval.KnowledgeSearchResult import KnowledgeSearchResult
from backend.tools.Tool import Tool
from backend.orchestration.Capability import Capability
from backend.tools.results.ToolResult import ToolResult


class KnowledgeSearchTool(Tool):
    """Executes knowledge search."""

    service: KnowledgeSearchService

    def __init__(
        self,
        service: KnowledgeSearchService
    ) -> None:
        """Initialize the knowledge search tool."""
        self.service = service

#------------- END of init () -----------------

    def execute(
        self,
        context: ExecutionContext
    ) -> ToolResult:
        """Execute the tool."""

        return self.service.search(
            context
        )

    @property
    def capability(self) -> Capability:
        """Business capability implemented by this tool."""

        return Capability.SEARCH_KNOWLEDGE