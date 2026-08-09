"""
Compliance Planner.

Type:
    Planning Strategy

Purpose:
    Creates the execution plan for compliance-related requests.

Responsibilities:
    - Build the ordered capability list required to satisfy a compliance request.

Does NOT:
    - Execute tools
    - Detect intent
    - Evaluate compliance rules
"""

from backend.intents.Intent import Intent
from backend.orchestration.Capability import Capability
from backend.orchestration.ExecutionPlan import ExecutionPlan
from backend.planning.Planner import Planner


class CompliancePlanner(Planner):
    """
    Planner for compliance requests.
    """

    def create_plan(
        self,
        intent: Intent
    ) -> ExecutionPlan:
        """
        Build the execution plan for compliance requests.
        """

        return ExecutionPlan(
            capabilities=[
                Capability.GENERATE_CHECKLIST
            ]
        )