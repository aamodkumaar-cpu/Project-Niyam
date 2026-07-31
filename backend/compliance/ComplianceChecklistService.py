"""
Compliance Checklist Service.

Purpose:
    Generates compliance checklists.

Responsibilities:
    - Generate compliance checklist

Does NOT:
    - Read PDFs
    - Call the LLM
"""

from pickle import TRUE
from backend.compliance.BusinessProfile import BusinessProfile
from backend.compliance.ComplianceChecklist import ComplianceChecklist
from backend.compliance.ComplianceItem import ComplianceItem
from backend.compliance.ComplianceRuleEngine import ComplianceRuleEngine

from backend.compliance.ComplianceRuleEngine import (
    ComplianceRuleEngine
)


class ComplianceChecklistService:

        """Generates compliance checklists."""

        def __init__(
            self
        ):
            """Initialize the compliance checklist service."""
            self.rule_engine = (
                ComplianceRuleEngine()
            )



        def generate(
            self,
            business_profile: BusinessProfile
        ) -> ComplianceChecklist:
            """Generate a compliance checklist."""
            applicable_rules = self.rule_engine.evaluate(
                business_profile
            )

            items = []
            for applicable_rule in applicable_rules:
                items.append(
                    ComplianceItem(
                        title=applicable_rule.rule.title,
                        description=applicable_rule.rule.description,
                        mandatory=True
                    )
                )

            return ComplianceChecklist(
                items=items
            )