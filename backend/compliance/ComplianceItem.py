"""
Compliance Item.

Purpose:
    Represents a single compliance requirement.

Responsibilities:
    - Store compliance information

Does NOT:
    - Execute compliance
    - Validate rules
"""

from dataclasses import dataclass


@dataclass
class ComplianceItem:
    """Represents one compliance requirement."""

    title: str
    description: str
    mandatory: bool