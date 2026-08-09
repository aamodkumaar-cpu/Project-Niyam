"""
Answer Formatter Service.

Purpose:
    Converts the final workflow result into the response shown to the user.

Responsibilities:
    - Read the previous tool result.
    - Produce the final presentation.

Does NOT:
    - Execute tools.
    - Search knowledge.
    - Call the LLM.
    - Perform orchestration.
"""

from backend.orchestration.ExecutionContext import ExecutionContext
from backend.tools.results.ToolResult import ToolResult


class AnswerFormatterService:
    """Converts the workflow result into the final answer."""

    def format(
        self,
        context: ExecutionContext
    ) -> ToolResult:
        """Format the final workflow result."""

        if context.previous_result is None:
            raise RuntimeError(
                "No previous tool result available."
            )

        return context.previous_result