"""
Request Context.

Purpose:
    Carries all information required to process one user request.

Responsibilities:
    - Store the user's question
    - Store the active business profile
    - Store search filters

Does NOT:
    - Execute business logic
    - Retrieve documents
    - Call the LLM
"""

from dataclasses import dataclass

from chromadb.types import Where
from backend.compliance.BusinessProfile import BusinessProfile



@dataclass
class RequestContext:
    question: str
    business_profile: BusinessProfile
    where: Where | None = None