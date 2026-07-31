"""
Business Profile.

Purpose:
    Represents a business seeking compliance guidance.

Responsibilities:
    - Store business information

Does NOT:
    - Validate business rules
    - Determine compliance
"""

from dataclasses import dataclass


@dataclass
class BusinessProfile:
    """Represents a business profile."""

    business_name: str
    industry: str
    company_size: int
    state: str