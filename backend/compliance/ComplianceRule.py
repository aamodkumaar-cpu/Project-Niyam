"""
Compliance Rule.

Purpose:
    Represents a single compliance rule.

Responsibilities:
    - Store rule information
    - Describe when a rule applies

Does NOT:
    - Evaluate itself
    - Read documents
    - Generate checklists
"""

from dataclasses import dataclass

@dataclass
class ComplianceRule:
    id: str
    title: str
    description: str
    minimum_employees: int