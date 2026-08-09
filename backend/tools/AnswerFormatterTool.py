"""
Answer Formatter Tool.

Type:
    Tool Adapter

Purpose:
    Formats a raw answer into the final presentation.

Responsibilities:
    - Delegate formatting to AnswerFormatterService

Does NOT:
    - Search documents
    - Call repositories
    - Execute business logic
"""

from backend.orchestration.ExecutionContext import ExecutionContext
from backend.presentation.AnswerFormatterService import AnswerFormatterService
from backend.tools.Tool import Tool
from backend.orchestration.Capability import Capability
from backend.tools.results.ToolResult import ToolResult


class AnswerFormatterTool(Tool):
    """Formats the final answer."""

    service: AnswerFormatterService

    def __init__(
        self,
        service: AnswerFormatterService
    ) -> None:
        """Initialize the formatter tool."""

        self.service = service

    def execute(
        self,
        context: ExecutionContext
    ) -> ToolResult:
        """Execute the formatter."""

        return self.service.format(
            context
        )

    @property
    def capability(self) -> Capability:
        """Business capability implemented by this tool."""

        return Capability.FORMAT_RESPONSE