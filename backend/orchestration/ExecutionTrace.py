"""
Execution Trace.

Type:
    Data Model

Purpose:
    Represents the execution history of one request.

Responsibilities:
    - Store execution records
    - Preserve execution order

Does NOT:
    - Execute tools
    - Measure execution
    - Log information
"""


from dataclasses import dataclass, field

from backend.orchestration.ExecutionRecord import ExecutionRecord


@dataclass
class ExecutionTrace:
    """Execution history for one request."""

    records: list[ExecutionRecord] = field(
        default_factory=list
    )