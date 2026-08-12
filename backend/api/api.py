"""
Project Niyam API.

Type:
API Boundary

Purpose:
Expose the Niyam application through HTTP.

Responsibilities:
- Create the FastAPI application.
- Initialize the Niyam application runtime.
- Expose health information.
- Accept business profile configuration.
- Accept user questions.
- Translate API requests into application calls.
- Translate application results into API responses.

Does NOT:
- Implement business logic.
- Retrieve knowledge.
- Call the LLM.
- Perform extraction.
- Execute tools directly.
- Contain customer-specific logic.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.NiyamApplication import (
    NiyamApplication,
    NiyamApplicationContract,
)
from backend.api.schemas.RequestSchemas import (
    BusinessProfileRequest,
    QuestionRequest,
)
from backend.api.schemas.ResponseSchemas import (
    HealthResponse,
    QuestionResponse,
    SourceResponse,
)
from backend.bootstrap.ServiceRegistry import ServiceRegistry
from backend.compliance.BusinessProfile import BusinessProfile


def create_application() -> NiyamApplication:
    """Create the configured Niyam application."""

    return NiyamApplication(
        registry=ServiceRegistry()
    )


def create_api(
    application: NiyamApplicationContract,
) -> FastAPI:
    """Create the FastAPI application around the application boundary."""

    @asynccontextmanager
    async def lifespan(
        api: FastAPI,
    ):
        """Initialize and finalize the Niyam application runtime."""

        application.initialize()

        yield

    api = FastAPI(
        title="Project Niyam",
        description="AI Compliance Officer for Indian SMBs",
        version="0.7.0",
        lifespan=lifespan,
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.get(
        "/api/v1/health",
        response_model=HealthResponse,
    )
    def health() -> HealthResponse:
        """Return API health information."""

        return HealthResponse(
            status="healthy"
        )

    @api.post(
        "/api/v1/profile",
    )
    def configure_profile(
        request: BusinessProfileRequest,
    ) -> dict[str, str]:
        """Configure the active business profile."""

        application.configure_business_profile(
            BusinessProfile(
                business_name=request.business_name,
                industry=request.industry,
                company_size=request.company_size,
                state=request.state,
            )
        )

        return {
            "status": "configured"
        }

    @api.post(
        "/api/v1/questions",
        response_model=QuestionResponse,
    )
    def ask_question(
        request: QuestionRequest,
    ) -> QuestionResponse:
        """Process a user question."""

        result = application.ask(
            question=request.question
        )

        if result.answer is None:
            raise RuntimeError(
                "Niyam did not produce an answer."
            )

        return QuestionResponse(
            answer=result.answer.answer,
            sources=[
                SourceResponse(
                    document_id=source.document_id,
                    source=source.source,
                    page_number=source.page_number,
                )
                for source in result.answer.sources
            ],
        )

    return api


application = create_application()

app = create_api(
    application=application
)