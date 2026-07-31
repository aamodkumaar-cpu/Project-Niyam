"""
Business Profile Collector.

Purpose:
    Collects business profile information from the user.

Responsibilities:
    - Collect business details
    - Build a BusinessProfile object

Does NOT:
    - Determine compliance
    - Call the LLM
    - Read documents
"""

from backend.compliance.BusinessProfile import BusinessProfile


class BusinessProfileCollector:
    def __init__(
        self
    ):
        """Initialize the business profile collector."""
        

    def collect(
        self
    ) -> BusinessProfile:

        """Collect a business profile."""

        business_name = input( "Business Name: " ).strip()
        state = input( "State: " ).strip()
        industry = input( "Industry: " ).strip()

        while True:
            try:
                company_size = int( input( "Number of Employees: ") )
                break
            except ValueError:
                print(  "Please enter a valid number." )

        return BusinessProfile(
            business_name=business_name,
            state=state,
            industry=industry,
            company_size=company_size
        )