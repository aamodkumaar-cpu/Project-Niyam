"""
Execution Monitor.

Type:
    Infrastructure

Purpose:
    Observes execution of workflow steps.

Responsibilities:
    - Record execution start
    - Record execution completion
    - Record execution failures
    - Measure execution duration

Does NOT:
    - Execute tools
    - Create plans
    - Retry failures
"""


from time import perf_counter
import time
from backend.orchestration.ExecutionTrace import ExecutionTrace
from backend.orchestration.ExecutionRecord import ExecutionRecord


class ExecutionMonitor:
    """Monitors workflow execution."""

    def __init__(self):
        """Initialize the monitor."""
        self.execution_trace = ExecutionTrace()

#----------- END of init() --------------------


    def start_step(
        self,
        step_name: str
    ) -> float:
        """Record step start."""

        print(f"\n▶ {step_name}")
        return perf_counter()


    def finish_step(
    self,
        step_name: str,
        started_at: float
    ):
        """Record successful execution."""

        duration = perf_counter() - started_at
        self.execution_trace.add(
            ExecutionRecord(
                step_name=step_name,
                status="SUCCESS",
                duration=duration
            )
        )


    def fail_step(
        self,
        step_name: str,
        error: Exception
    ):
        """Record failed execution."""

        self.execution_trace.add(
            ExecutionRecord(
                step_name=step_name,
                status="FAILED",
                duration=0,
                message=str(error)
            )
        )


    def skip_step(
        self,
        step_name: str,
        reason: str
    ):
        """Record skipped execution."""

        self.execution_trace.add(
            ExecutionRecord(
                step_name=step_name,
                status="SKIPPED",
                duration=0,
                message=reason
            )
        )




    def get_execution_trace(
        self
    ) -> ExecutionTrace:
        """Return execution trace."""

        return self.execution_trace