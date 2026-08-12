"""
API Response Schemas.

Type:
    API Contract

Purpose:
    Define generic response models returned by the Project Niyam API.

Responsibilities:
    - Represent health information.
    - Represent question responses.
    - Represent source attribution.
    - Provide stable contracts for API clients.

Does NOT:
    - Execute business logic.
    - Retrieve knowledge.
    - Call the LLM.
    - Perform compliance analysis.
    - Know anything about a specific customer or document.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Represents the API health response."""

    status: str


class SourceResponse(BaseModel):
    """Represents source metadata associated with an answer."""

    document_id: str
    source: str
    page_number: int


class QuestionResponse(BaseModel):
    """Represents the response to a user question."""

    answer: str
    sources: list[SourceResponse]