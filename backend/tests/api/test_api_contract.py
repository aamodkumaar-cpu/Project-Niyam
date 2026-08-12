"""
API Contract Tests.

Purpose:
    Protect the HTTP response contract exposed by Project Niyam.

Responsibilities:
    - Verify question response structure.
    - Verify source attribution structure.
    - Verify required source metadata.

Does NOT:
    - Test retrieval internals.
    - Test extraction internals.
    - Call Ollama.
    - Depend on a real document set.
"""

from backend.api.schemas.ResponseSchemas import (
    QuestionResponse,
    SourceResponse,
)


def test_question_response_contains_answer_and_sources() -> None:
    """Verify that question responses contain answer and sources."""

    response = QuestionResponse(
        answer="Built a billing platform.",
        sources=[
            SourceResponse(
                document_id="company-a",
                source="Company-A.pdf",
                page_number=1,
            )
        ],
    )

    assert response.answer == "Built a billing platform."
    assert len(response.sources) == 1


def test_source_response_contains_document_location() -> None:
    """Verify that source responses preserve document location."""

    source = SourceResponse(
        document_id="company-a",
        source="Company-A.pdf",
        page_number=1,
    )

    assert source.document_id == "company-a"
    assert source.source == "Company-A.pdf"
    assert source.page_number == 1