"""
Execution Step.

Type:
    Workflow Model

Purpose:
    Represents a single step within an execution plan.

Responsibilities:
    - Store the capability to execute.

Does NOT:
    - Execute the capability.
    - Know which tool implements the capability.
    - Perform orchestration.
"""

from dataclasses import dataclass
from backend.orchestration.Capability import Capability


@dataclass(frozen=True)
class ExecutionStep:
    """
    Represents one executable workflow step.
    """
    capability: Capability