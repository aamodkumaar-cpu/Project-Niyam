"""
Workflow Executor.

Purpose:
    Executes an ExecutionPlan by invoking the corresponding tools
    in sequence.

Responsibilities:
    - Execute capabilities in order.
    - Retrieve tools from the ToolRegistry.
    - Pass the shared ExecutionContext to each tool.
    - Store the previous ToolResult in the ExecutionContext.
    - Return the final ToolResult.

Does NOT:
    - Decide what should be executed.
    - Perform planning.
    - Contain business logic.
    - Call services directly.
"""

from backend.orchestration.ExecutionContext import ExecutionContext
from backend.orchestration.ExecutionPlan import ExecutionPlan
from backend.tools.ToolRegistry import ToolRegistry
from backend.tools.results.ToolResult import ToolResult


class WorkflowExecutor:
    """
    Executes an execution plan.
    """

    def __init__(
        self,
        tool_registry: ToolRegistry
    ):
        self.tool_registry = tool_registry

# ---------------- END __init__ ----------------

    def execute(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext
    ) -> ToolResult:

        if not plan.capabilities:
            raise ValueError(
                "ExecutionPlan contains no capabilities."
            )

        first_tool = self.tool_registry.get(
            plan.capabilities[0]
        )

        result = first_tool.execute(context)
        context.previous_result = result

        for capability in plan.capabilities[1:]:

            tool = self.tool_registry.get(capability)

            result = tool.execute(context)

            context.previous_result = result

        return result

# ---------------- END execute ----------------