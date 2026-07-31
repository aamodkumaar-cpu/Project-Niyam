"""
Compliance Rule Repository.

Purpose:
    Provides all available compliance rules.

Responsibilities:
    - Load compliance rules
    - Return available rules

Does NOT:
    - Evaluate rules
    - Generate checklists
    - Call the LLM
"""

from backend.compliance.ComplianceRule import ComplianceRule


class ComplianceRuleRepository:
    def __init__(
        self
    ):
        """Initialize the compliance rule repository."""


    def get_all(
        self
    ) -> list[ComplianceRule]:

        """Return all compliance rules."""
        return [
            ComplianceRule(
                id="EPF-001",
                title="EPF Registration",
                description=(
                    "Register under the Employees' "
                    "Provident Fund."
                ),
                minimum_employees=20
            ),
            ComplianceRule(
                id="ESIC-001",
                title="ESIC Registration",
                description=(
                    "Register under the Employees' "
                    "State Insurance Scheme."
                ),
                minimum_employees=10
            ),
            ComplianceRule(
                id="SEA-001",
                title="Shops & Establishments Registration",
                description=(
                    "Register under the applicable "
                    "State Shops and Establishments Act."
                ),
                minimum_employees=1
            )
        ]