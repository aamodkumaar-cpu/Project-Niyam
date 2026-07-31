"""
Business Profile Session.

Purpose:
    Stores the active business profile for the current application session.

Responsibilities:
    - Store the current business profile
    - Return the current business profile

Does NOT:
    - Collect user input
    - Persist data
    - Generate compliance results
"""

from backend.compliance.BusinessProfile import BusinessProfile

class BusinessProfileSession:
    def __init__(
        self
    ):
        """Initialize the business profile session."""

        self._business_profile = None


    def set_business_profile(
        self,
        business_profile: BusinessProfile
    ) -> None:
        """Store the active business profile."""

        self._business_profile = business_profile


    def get_business_profile(
        self
    ) -> BusinessProfile:
        """Return the active business profile."""

        if self._business_profile is None:
            raise RuntimeError(
            "Business profile not initialized."
        )

        return self._business_profile