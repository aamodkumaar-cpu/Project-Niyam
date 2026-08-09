"""
Execution Planner.

Type:
    Planner Director

Purpose:
    Selects the appropriate planner strategy.

Responsibilities:
    - Select the planner
    - Delegate plan creation

Does NOT:
    - Execute tools
    - Build workflows directly
    - Detect intent
"""

from backend.intents.Intent import Intent
from backend.intents.IntentType import IntentType
from backend.orchestration.ExecutionPlan import ExecutionPlan

from backend.planning.KnowledgePlanner import KnowledgePlanner
from backend.planning.CompliancePlanner import CompliancePlanner


class ExecutionPlanner:
    """Delegates planning to specialized planners."""

    def __init__(self):

        self.planners = {
            IntentType.QUESTION: KnowledgePlanner(),
            IntentType.COMPLIANCE_CHECKLIST: CompliancePlanner()
        }

    def create_plan(
        self,
        intent: Intent
    ) -> ExecutionPlan:
        """Create an execution plan."""

        planner = self.planners.get(intent.type)

        if planner is None:
            raise ValueError(
                f"No planner registered for {intent.type}"
            )

        return planner.create_plan(intent)