"""
Execution Plan.

Purpose:
    Represents the sequence of capabilities that should be executed
    to satisfy a user's request.

Responsibilities:
    - Store the ordered list of capabilities.
    - Act as the contract between the Planner and WorkflowExecutor.

Does NOT:
    - Execute tools.
    - Perform planning.
    - Contain business logic.
"""

from dataclasses import dataclass

from backend.orchestration.Capability import Capability


@dataclass(slots=True)
class ExecutionPlan:
    """
    Ordered list of capabilities to execute.
    """

    capabilities: list[Capability]