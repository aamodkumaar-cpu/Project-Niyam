"""
Execution Executor.

Type:
    Application Service

Purpose:
    Executes an execution plan.

Responsibilities:
    - Execute tools in the execution plan
    - Maintain the execution context
    - Record execution progress
    - Return the final execution result

Does NOT:
    - Create execution plans
    - Detect user intent
    - Implement tool business logic
"""

from backend.orchestration.ExecutionContext import ExecutionContext
from backend.orchestration.ExecutionMonitor import ExecutionMonitor
from backend.orchestration.ExecutionPlan import ExecutionPlan
from backend.orchestration.ExecutionResult import ExecutionResult
from backend.orchestration.RequestContext import RequestContext
from backend.tools.ToolRegistry import ToolRegistry
from backend.tools.results.ToolResult import ToolResult


class ExecutionExecutor:
    """Executes an execution plan."""

    tool_registry: ToolRegistry
    execution_monitor: ExecutionMonitor

    def __init__(
        self,
        tool_registry: ToolRegistry,
        execution_monitor: ExecutionMonitor
    ) -> None:
        """Initialize the execution executor."""

        self.tool_registry = tool_registry
        self.execution_monitor = execution_monitor

    # ---------- Public ----------

    def execute(
        self,
        plan: ExecutionPlan,
        context: RequestContext
    ) -> ExecutionResult:
        """
        Execute the supplied execution plan.
        """

        execution_context = ExecutionContext(
            request=context
        )

        result: ToolResult | None = None

        for capability in plan.capabilities:

            tool = self.tool_registry.get(
                capability
            )

            step_name = tool.__class__.__name__

            started_at = self.execution_monitor.start_step(
                step_name
            )

            try:

                result = tool.execute(
                    execution_context
                )

                execution_context.previous_result = result

                self.execution_monitor.finish_step(
                    step_name=step_name,
                    started_at=started_at
                )

            except Exception as error:

                self.execution_monitor.fail_step(
                    step_name=step_name,
                    error=error
                )

                raise

        assert result is not None

        return ExecutionResult(
            result=result,
            trace=self.execution_monitor.get_execution_trace()
        )