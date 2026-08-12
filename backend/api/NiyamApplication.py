"""
Niyam Application.

Type:
    Application Service

Purpose:
    Provides the application boundary for Project Niyam.

Responsibilities:
    - Initialize the application runtime.
    - Configure the active business profile.
    - Accept user questions.
    - Return application execution results.

Does NOT:
    - Implement business logic.
    - Retrieve knowledge directly.
    - Build prompts.
    - Call the LLM directly.
    - Know anything about HTTP or FastAPI.
"""

from __future__ import annotations

from typing import Protocol

from backend.bootstrap.ServiceRegistry import ServiceRegistry
from backend.compliance.BusinessProfile import BusinessProfile
from backend.orchestration.ExecutionResult import ExecutionResult


class NiyamApplicationContract(Protocol):
    """Defines the application boundary required by external interfaces."""

    def initialize(self) -> None:
        """Initialize the Niyam application runtime."""
        ...

    def configure_business_profile(
        self,
        business_profile: BusinessProfile,
    ) -> None:
        """Configure the active business profile."""
        ...

    def ask(
        self,
        question: str,
    ) -> ExecutionResult:
        """Process a user question through the Niyam runtime."""
        ...


class NiyamApplication:
    """Provides the application boundary for Project Niyam."""

    registry: ServiceRegistry
    initialized: bool

    def __init__(
        self,
        registry: ServiceRegistry | None = None,
    ) -> None:
        """Initialize the application boundary."""

        self.registry = (
            registry
            if registry is not None
            else ServiceRegistry()
        )

        self.initialized = False

    def initialize(self) -> None:
        """Initialize the knowledge base and application runtime."""

        if self.initialized:
            return

        documents = self.registry.document_service.list_documents()

        for document in documents:
            self.registry.ingestion_service.ingest_document(
                document
            )

        self.initialized = True

    def configure_business_profile(
        self,
        business_profile: BusinessProfile,
    ) -> None:
        """Configure the active business profile."""

        self.registry.business_profile_session.set_business_profile(
            business_profile
        )

    def ask(
        self,
        question: str,
    ) -> ExecutionResult:
        """Process a user question through the Niyam runtime."""

        if not self.initialized:
            raise RuntimeError(
                "NiyamApplication has not been initialized."
            )

        return self.registry.request_router.route(
            question=question
        )