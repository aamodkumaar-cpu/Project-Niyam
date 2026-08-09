"""
Execution Result.

Type:
    Runtime Model

Purpose:
    Represents the complete outcome of an execution.

Responsibilities:
    - Store the final answer
    - Store execution trace

Does NOT:
    - Execute workflow steps
"""

from dataclasses import dataclass, field

from backend.results.AnswerResult import AnswerResult
from backend.orchestration.ExecutionTrace import ExecutionTrace
from backend.tools.results.ToolResult import ToolResult


@dataclass(slots=True)
class ExecutionResult:

    result: ToolResult

    trace: ExecutionTrace

    answer: AnswerResult | None = field(
        default=None,
        init=False
    )