"""
Compliance Checklist.

Purpose:
    Represents the compliance requirements for a business.

Responsibilities:
    - Store compliance items

Does NOT:
    - Generate compliance rules
"""

from dataclasses import dataclass, field
from backend.compliance.ComplianceItem import ComplianceItem
from backend.tools.results.ToolResult import ToolResult


@dataclass
class ComplianceChecklist(ToolResult):
    """Represents a compliance checklist."""

    items: list[ComplianceItem] = field(default_factory=list)