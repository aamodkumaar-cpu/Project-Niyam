"""
Execution Context.

Type:
    Runtime Context

Purpose:
    Carries all shared information required while executing an
    workflow.

Responsibilities:
    - Store the original request
    - Store the previous step result
    - Store shared workflow data

Does NOT:
    - Execute workflow steps
    - Perform planning
    - Store business logic
"""

from dataclasses import dataclass
from backend.orchestration.RequestContext import RequestContext
from backend.tools.results.ToolResult import ToolResult


@dataclass
class ExecutionContext:
    """Shared context for an execution workflow."""

    request: RequestContext
    previous_result: ToolResult | None = None
