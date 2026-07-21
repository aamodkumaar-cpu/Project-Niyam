"""
Business Profile.

Purpose:
    Represents the business information required for compliance.

Responsibilities:
    - Store business profile information

Does NOT:
    - Perform compliance evaluation
    - Read documents
"""

from dataclasses import dataclass


@dataclass
class BusinessProfile:
    """Represents a business profile."""

    company_size: int
    state: str