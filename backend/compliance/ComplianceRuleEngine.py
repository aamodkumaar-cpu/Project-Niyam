"""
Compliance Rule Engine.

Purpose:
    Determines applicable compliance requirements for a business.

Responsibilities:
    - Evaluate compliance rules
    - Return applicable checklist items

Does NOT:
    - Call the LLM
    - Read documents
    - Generate explanations
"""

from backend.compliance.ApplicableRule import ApplicableRule
from backend.compliance.BusinessProfile import BusinessProfile
from backend.compliance.ComplianceChecklist import ComplianceChecklist
from backend.compliance.ComplianceRuleRepository import ComplianceRuleRepository


class ComplianceRuleEngine:
    def __init__(
        self
    ):
        """Initialize the compliance rule engine."""
        self.rule_repository = (
            ComplianceRuleRepository()
        )

    def evaluate(
        self,
        business_profile: BusinessProfile
    ) -> list[ApplicableRule]:
        """Evaluate compliance rules."""

        rules = self.rule_repository.get_all()

        applicable_rules = []

        for rule in rules:
            if ( business_profile.company_size >= rule.minimum_employees ):
                applicable_rules.append(
                    ApplicableRule(
                        rule=rule,
                        reason=(
                            f"Business has "
                            f"{business_profile.company_size} "
                            f"employees."
                        )
                    )
                )

        return applicable_rules