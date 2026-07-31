"""
Execution Executor.

Purpose:
    Executes an execution plan.

Responsibilities:
    - Execute plan steps
    - Invoke application tools

Does NOT:
    - Create plans
    - Detect intent
    - Call the LLM directly
"""


from backend.orchestration.ExecutionMonitor import ExecutionMonitor
from backend.orchestration.ExecutionPlan import ExecutionPlan
from backend.orchestration.RequestContext import RequestContext
from backend.tools.ToolRegistry import ToolRegistry
from backend.orchestration.ExecutionResult import ExecutionResult
from backend.orchestration.ExecutionContext import ExecutionContext



class ExecutionExecutor:
    """Executes an execution plan."""


    def __init__(
        self
    ):
        """Initialize the executor."""

        self.tool_registry = ToolRegistry()
        self.execution_monitor = ExecutionMonitor()

# --------- END of init() -----------------

    def execute(
        self,
        plan: ExecutionPlan,
        context: RequestContext
    ):
        """Execute the plan."""

        result = None
        execution_context = ExecutionContext(
                                request=context,
                                shared_data={}
                            )

        for step in plan.steps:
            started_at = self.execution_monitor.start_step( step.description )

            try:
                tool = self.tool_registry.get( step.tool_name  )
                result = tool.execute(execution_context)
                self.execution_monitor.finish_step(
                    step.description,
                    started_at
                )
            except Exception as error:
                self.execution_monitor.fail_step(
                    step.description,
                    error
                )
                raise

        return ExecutionResult(
            result=result,
            trace=self.execution_monitor.get_execution_trace()
        )