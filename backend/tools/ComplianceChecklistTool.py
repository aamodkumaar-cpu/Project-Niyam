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

from backend.tools.Tool import Tool
from backend.compliance.ComplianceChecklistService import  ComplianceChecklistService
from backend.orchestration.RequestContext import  RequestContext


class ComplianceChecklistTool(Tool):
    def __init__(
        self
    ):
        """Initialize the compliance checklist tool."""

        self.service = ComplianceChecklistService()

    

    def execute(
        self,
        context: RequestContext
    ):
        """Execute the tool."""

        return self.service.generate(
            context.business_profile
        )