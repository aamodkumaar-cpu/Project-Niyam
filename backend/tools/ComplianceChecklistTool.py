"""
Compliance Checklist Tool.

Purpose:
    Executes compliance checklist generation.

Responsibilities:
    - Generate a compliance checklist

Does NOT:
    - Evaluate compliance rules
    - Retrieve documents
    - Call the LLM
"""

from backend.orchestration.ExecutionContext import ExecutionContext
from backend.tools.Tool import Tool
from backend.compliance.ComplianceChecklistService import  ComplianceChecklistService
from backend.orchestration.Capability import Capability
from backend.tools.results.ComplianceChecklistResult import ComplianceChecklistResult
from backend.tools.results.ToolResult import ToolResult


class ComplianceChecklistTool(Tool):
    """Generates compliance checklists."""

    service: ComplianceChecklistService

    def __init__(
        self,
        service: ComplianceChecklistService
    ) -> None:
        """Initialize the tool."""

        self.service = service

    @property
    def capability(self) -> Capability:
        """Business capability implemented by this tool."""

        return Capability.GENERATE_CHECKLIST

    def execute(
        self,
        context: ExecutionContext
    ) -> ToolResult:
        """Execute the tool."""

        checklist = self.service.generate(
            context.request.business_profile
        )

        return ComplianceChecklistResult(
            checklist
        )