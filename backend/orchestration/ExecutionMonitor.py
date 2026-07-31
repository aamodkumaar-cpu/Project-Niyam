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
    ) -> None:
        """Record successful completion."""

        duration = perf_counter() - started_at
        self.execution_trace.records.append(
            ExecutionRecord(
                step_name=step_name,
                duration=duration,
                successful=True
            )
        )

        print(
            f"✔ {step_name} ({duration:.2f}s)"
        )


    def fail_step(
        self,
        step_name: str,
        error: Exception
    ) -> None:
        """Record failed execution."""
        self.execution_trace.records.append(
            ExecutionRecord(
                step_name=step_name,
                duration=0.0,
                successful=False
            )
        )
        print( f"✖ {step_name}: {error}"  )


    def get_execution_trace(
        self
    ) -> ExecutionTrace:
        """Return the execution trace."""

        return self.execution_trace