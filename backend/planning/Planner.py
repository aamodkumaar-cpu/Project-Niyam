"""
Planner.

Type:
    Planning Strategy

Purpose:
    Defines the contract for all execution planners.

Responsibilities:
    - Create an execution plan

Does NOT:
    - Execute tools
    - Detect intent
    - Build responses
"""

from abc import ABC, abstractmethod

from backend.intents.Intent import Intent
from backend.orchestration.ExecutionPlan import ExecutionPlan


class Planner(ABC):
    """Base planner."""

    @abstractmethod
    def create_plan(
        self,
        intent: Intent
    ) -> ExecutionPlan:
        """Create an execution plan."""
        raise NotImplementedError