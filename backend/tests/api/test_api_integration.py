"""
API Integration Tests.

Purpose:
    Verify the HTTP boundary delegates correctly to the
    Project Niyam application boundary.

Responsibilities:
    - Verify API startup.
    - Verify health endpoint behavior.
    - Verify business profile configuration.
    - Verify question request handling.
    - Verify answer and source metadata survive the API boundary.

Does NOT:
    - Call Ollama.
    - Access ChromaDB.
    - Ingest real documents.
    - Test retrieval internals.
"""

from dataclasses import dataclass

from fastapi.testclient import TestClient

from backend.api.api import create_api
from backend.api.NiyamApplication import NiyamApplicationContract
from backend.compliance.BusinessProfile import BusinessProfile
from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.orchestration.ExecutionResult import ExecutionResult
from backend.orchestration.ExecutionTrace import ExecutionTrace
from backend.results.AnswerResult import AnswerResult
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.tools.results.ToolResult import ToolResult


class FakeToolResult(ToolResult):
    """Provides a deterministic tool result for API testing."""


@dataclass
class FakeApplication:
    """Provides deterministic application behavior for API tests."""

    initialized: bool = False
    configured_profile: BusinessProfile | None = None

    def initialize(self) -> None:
        """Initialize the fake application."""

        self.initialized = True

    def configure_business_profile(
        self,
        business_profile: BusinessProfile,
    ) -> None:
        """Store the configured business profile."""

        self.configured_profile = business_profile

    def ask(
        self,
        question: str,
    ) -> ExecutionResult:
        """Return a deterministic execution result."""

        result = ExecutionResult(
            result=FakeToolResult(),
            trace=ExecutionTrace(),
        )

        result.answer = AnswerResult(
            answer="Built a billing platform.",
            sources=[
                DocumentMetadata(
                    document_id="company-a",
                    source="Company-A.pdf",
                    domain=KnowledgeDomain.GENERAL,
                    compliance_pack="",
                    page_number=1,
                    chunk_number=0,
                )
            ],
        )

        return result


def _create_client() -> TestClient:
    """Create a test client using a deterministic application."""

    application: NiyamApplicationContract = FakeApplication()

    api = create_api(
        application=application
    )

    return TestClient(
        api
    )


def test_health_endpoint() -> None:
    """Verify the health endpoint."""

    client = _create_client()

    response = client.get(
        "/api/v1/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_profile_endpoint() -> None:
    """Verify business profile configuration."""

    client = _create_client()

    response = client.post(
        "/api/v1/profile",
        json={
            "business_name": "Company A",
            "industry": "Manufacturing",
            "company_size": 50,
            "state": "Delhi",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "configured"
    }


def test_question_endpoint_returns_answer_and_sources() -> None:
    """Verify question responses contain answer and source metadata."""

    client = _create_client()

    response = client.post(
        "/api/v1/questions",
        json={
            "question": "What did Company A accomplish?"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["answer"] == (
        "Built a billing platform."
    )

    assert body["sources"] == [
        {
            "document_id": "company-a",
            "source": "Company-A.pdf",
            "page_number": 1,
        }
    ]