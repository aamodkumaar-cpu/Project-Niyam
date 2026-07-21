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

from backend.compliance.BusinessProfile import BusinessProfile
from backend.compliance.ComplianceChecklist import ComplianceChecklist
from backend.compliance.ComplianceItem import ComplianceItem


class ComplianceChecklistService:
    """Generates compliance checklists."""

    def generate(
        self,
        business_profile: BusinessProfile
    ) -> ComplianceChecklist:
        """Generate a compliance checklist."""
        checklist = ComplianceChecklist()

        if business_profile.company_size >= 1:
            checklist.items.append(
                ComplianceItem(
                    title="Appointment Letters",
                    description="Issue appointment letters to all employees.",
                    mandatory=True
                )
            )

        if business_profile.company_size >= 10:
            checklist.items.append(
                ComplianceItem(
                    title="PF Registration",
                    description="Register under the Employees' Provident Fund.",
                    mandatory=True
                )
            )

            checklist.items.append(
                ComplianceItem(
                    title="ESIC Registration",
                    description="Register under the Employees' State Insurance Scheme.",
                    mandatory=True
                )
            )

        return checklist