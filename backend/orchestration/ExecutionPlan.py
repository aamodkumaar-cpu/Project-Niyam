"""
Execution Plan.

Purpose:
    Represents the sequence of actions required
    to satisfy a user request.

Responsibilities:
    - Store execution steps

Does NOT:
    - Execute steps
    - Route requests
"""

from dataclasses import dataclass
from backend.orchestration.ExecutionStep import ExecutionStep


@dataclass
class ExecutionPlan:
    
    """Represents an execution plan."""
    steps: list[ExecutionStep]