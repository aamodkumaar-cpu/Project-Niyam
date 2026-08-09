"""
Answer Formatter Result.

Purpose:
    Represents the formatted answer produced by the presentation layer.

Responsibilities:
    - Store the final formatted answer.
    - Act as the output of AnswerFormatterTool.

Does NOT:
    - Format answers.
    - Execute tools.
    - Build prompts.
"""

from dataclasses import dataclass

from backend.tools.results.ToolResult import ToolResult


@dataclass(slots=True)
class AnswerFormatterResult(ToolResult):
    """
    Final formatted response.
    """

    answer: str