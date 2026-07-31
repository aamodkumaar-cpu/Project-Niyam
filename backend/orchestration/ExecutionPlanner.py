"""
Execution Planner.

Purpose:
    Creates an execution plan for a user request.

Responsibilities:
    - Decide which steps are required
    - Build an execution plan

Does NOT:
    - Execute tools
    - Call the LLM
    - Retrieve documents
"""


from backend.orchestration.ExecutionPlan import ExecutionPlan
from backend.intents.Intent import Intent
from backend.intents.IntentType import IntentType
from backend.orchestration.ExecutionStep import ExecutionStep


class ExecutionPlanner:
    """Creates execution plans."""


    def create_plan(
        self,
        intent: Intent
    ) -> ExecutionPlan:
        """Create an execution plan."""

        if intent.type == IntentType.COMPLIANCE_CHECKLIST:

            return ExecutionPlan(
                steps=[
                    ExecutionStep(
                        tool_name="compliance_checklist",
                        input_data=None,
                        description="Generate compliance checklist"
                    )
                ]
            )

        return ExecutionPlan(
            steps=[
                ExecutionStep(
                    tool_name="knowledge_search",
                    description="Search the knowledge base"
                ),
                ExecutionStep(
                    tool_name="answer_formatter",
                    description="Format the final answer"
                )
            ]
        )