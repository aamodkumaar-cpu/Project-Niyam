"""
Execution Trace.

Type:
    Runtime Model

Purpose:
    Stores the complete execution history of one workflow.

Responsibilities:
    - Store execution records
    - Provide execution history

Does NOT:
    - Execute workflow steps
    - Print results
"""

from dataclasses import dataclass, field
from backend.orchestration.ExecutionRecord import ExecutionRecord


@dataclass
class ExecutionTrace:
    """Represents one workflow execution."""

    records: list[ExecutionRecord] = field(
        default_factory=list
    )

    def add(
        self,
        record: ExecutionRecord
    ):
        """Add one execution record."""

        self.records.append(record)