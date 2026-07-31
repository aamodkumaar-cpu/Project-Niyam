"""
Applicable Rule.

Purpose:
    Represents a compliance rule that applies to a business.

Responsibilities:
    - Store the applicable rule
    - Store the reason why the rule applies

Does NOT:
    - Evaluate rules
    - Generate checklists
"""

from dataclasses import dataclass
from backend.compliance.ComplianceRule import ComplianceRule


@dataclass
class ApplicableRule:
    rule: ComplianceRule
    reason: str