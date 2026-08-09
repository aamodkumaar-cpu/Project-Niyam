"""
Compliance Checklist Result.

Purpose:
    Represents the result produced by the Compliance Checklist Tool.

Responsibilities:
    - Carry the generated compliance checklist.
    - Provide a ToolResult for the orchestration layer.

Does NOT:
    - Generate the checklist.
    - Execute business logic.
    - Format responses.
"""

from backend.compliance.ComplianceChecklist import ComplianceChecklist
from backend.tools.results.ToolResult import ToolResult


class ComplianceChecklistResult(ToolResult):
    """
    Result returned by the Compliance Checklist Tool.
    """

    def __init__(
        self,
        checklist: ComplianceChecklist
    ):
        self.checklist = checklist
