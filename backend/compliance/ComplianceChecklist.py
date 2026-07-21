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


@dataclass
class ComplianceChecklist:
    """Represents a compliance checklist."""

    items: list[ComplianceItem] = field(default_factory=list)