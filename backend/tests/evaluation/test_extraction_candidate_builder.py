"""
Extraction Candidate Builder Tests.
"""

from pypdf import PdfReader

from backend.extraction.ExtractionCandidateBuilder import ExtractionCandidateBuilder
from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KnowledgeNode import KnowledgeNode


def _node(content: str) -> KnowledgeNode:
    """Create a test knowledge node."""

    return KnowledgeNode(
        content=content,
        score=1.0,
        metadata=DocumentMetadata(
            document_id="doc",
            source="doc.pdf",
            domain=KnowledgeDomain.GENERAL,
            compliance_pack="",
            page_number=1,
            chunk_number=0,
        ),
    )


def test_bullets_are_deterministic_candidates() -> None:
    """Create one source-owned candidate per explicit bullet."""

    candidates = ExtractionCandidateBuilder().build([
        _node(
            "Company A\n"
            "● Built platform.\n"
            "● Reduced latency by 40%."
        )
    ])

    assert [candidate.candidate_id for candidate in candidates] == [
        "C1_1",
        "C1_2",
    ]

    assert candidates[0].source_quote == "Built platform."
    assert candidates[1].source_quote == "Reduced latency by 40%."

    assert candidates[0].heading == "Company A"
    assert candidates[1].heading == "Company A"


def test_multiple_sentences_are_split_into_atomic_candidates() -> None:
    """Split independently stated sentences from one bullet."""

    candidates = ExtractionCandidateBuilder().build([
        _node(
            "EARLY CAREER (Company A, Company B) | 2020-2022\n"
           + "● Built platform. Reduced latency by 40%."
        )
    ])

    assert [
        candidate.source_quote
        for candidate in candidates
    ] == [
        "Built platform.",
        "Reduced latency by 40%.",
    ]


def test_real_resume_structure_is_not_hardcoded() -> None:
    """Extract the supplied resume structure through generic source rules."""

    pdf = PdfReader(
        "backend/documents/Amod Kumar-Senior Engineering Leader.pdf"
    )

    node = KnowledgeNode(
        content=pdf.pages[1].extract_text(),
        score=1.0,
        metadata=DocumentMetadata(
            document_id="resume",
            source="Amod Kumar-Senior Engineering Leader.pdf",
            domain=KnowledgeDomain.GENERAL,
            compliance_pack="",
            page_number=2,
            chunk_number=3,
        ),
    )

    candidates = ExtractionCandidateBuilder().build(
        [node]
    )

    headings = {
        candidate.heading
        for candidate in candidates
    }

    assert (
        "Founder, Sonehaat.com " +
        "(June 2025-March 2026)"
        in headings
    )

    assert (
        "Senior Engineering Manager, Cloudera "
       + "(Oct 2022–Jun 2025)"
        in headings
    )

    assert (
        "Engineering Manager, 24[7].ai "
        +"(Mar 2021–Sep 2022)"
        in headings
    )

    assert (
        "Senior Engineering Manager, CDK Global "
       + "(May 2019–Feb 2021)"
        in headings
    )

    assert (
        "Software Development Manager, Oracle "
       + "(Nov 2006–May 2019)"
        in headings
    )

    assert any(
        "EARLY CAREER" in heading
        for heading in headings
    )