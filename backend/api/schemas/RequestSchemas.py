"""
API Request Schemas.

Type:
    API Contract

Purpose:
    Define generic request models accepted by the Project Niyam API.

Responsibilities:
    - Represent business profile input.
    - Represent user question input.
    - Validate API request structure.

Does NOT:
    - Execute business logic.
    - Retrieve knowledge.
    - Call the LLM.
    - Perform compliance analysis.
    - Know anything about a specific customer or document.
"""

from pydantic import BaseModel, Field


class BusinessProfileRequest(BaseModel):
    """Represents business profile information supplied by a client."""

    business_name: str = Field(
        min_length=1,
    )

    industry: str = Field(
        min_length=1,
    )

    company_size: int = Field(
        ge=1,
    )

    state: str = Field(
        min_length=1,
    )


class QuestionRequest(BaseModel):
    """Represents a user question submitted to Niyam."""

    question: str = Field(
        min_length=1,
    )