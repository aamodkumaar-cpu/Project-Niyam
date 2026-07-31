"""
Execution Result.

Type:
    Data Model (DTO)

Purpose:
    Represents the complete outcome of executing an execution plan.

Responsibilities:
    - Store the business result
    - Store the execution trace

Does NOT:
    - Execute workflow steps
    - Perform business logic
    - Transform results
"""


from dataclasses import dataclass
from typing import Any

from backend.orchestration.ExecutionTrace import ExecutionTrace


@dataclass
class ExecutionResult:
    """Represents the outcome of a workflow execution."""

    result: Any

    trace: ExecutionTrace