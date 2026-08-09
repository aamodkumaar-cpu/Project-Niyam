from backend.intents.Intent import Intent
from backend.orchestration.Capability import Capability
from backend.orchestration.ExecutionPlan import ExecutionPlan
from backend.planning.Planner import Planner


class KnowledgePlanner(Planner):
    """
    Planner for knowledge search requests.
    """

    def create_plan(
        self,
        intent: Intent
    ) -> ExecutionPlan:
        """
        Build the execution plan for knowledge retrieval.
        """

        return ExecutionPlan(
            capabilities=[
                Capability.SEARCH_KNOWLEDGE,
                Capability.FORMAT_RESPONSE
            ]
        )