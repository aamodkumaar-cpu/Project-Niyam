from backend.extraction.EvidenceRequirement import (
    EvidenceRequirement,
)
from backend.extraction.EvidenceSignalDetector import EvidenceSignalDetector
from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
from backend.extraction.ExtractionCandidateRanker import (
    ExtractionCandidateRanker,
)
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.ingestion.KnowledgeDomain import KnowledgeDomain


def _candidate(
    candidate_id: str,
    heading: str,
    structural_context: str,
    source_quote: str,
) -> ExtractionCandidate:
    """Create a deterministic extraction candidate for ranking tests."""

    node = KnowledgeNode(
        content=source_quote,
        score=1.0,
        metadata=DocumentMetadata(
            document_id="test",
            source="test.pdf",
            domain=KnowledgeDomain.GENERAL,
            compliance_pack="",
            page_number=1,
            chunk_number=1,
        ),
    )

    return ExtractionCandidate(
        candidate_id=candidate_id,
        heading=heading,
        structural_context=structural_context,
        source_quote=source_quote,
        node=node,
    )


def _ranker() -> ExtractionCandidateRanker:
    """Create the production candidate ranker."""

    return ExtractionCandidateRanker(
        keyword_tokenizer=KeywordTokenizer(),
        keyword_scorer=KeywordScorer(),
        evidence_signal_detector=EvidenceSignalDetector(),
    )


def test_ranker_prioritizes_candidate_whose_heading_matches_question_scope():
    """Prioritize candidates whose structural scope matches the question."""

    ranker = _ranker()

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="Senior Engineering Manager, Cloudera (Oct 2022–Jun 2025)",
            structural_context="Senior Engineering Manager, Cloudera (Oct 2022–Jun 2025)",
            source_quote=(
                "Led 25+ engineers including principal engineers, "
                "architects, and managers across India, US and Europe."
            ),
        ),
        _candidate(
            candidate_id="C2",
            heading="Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)",
            structural_context="Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)",
            source_quote="Led AI-powered customer engagement platforms.",
        ),
        _candidate(
            candidate_id="C3",
            heading="Software Development Manager, Oracle (Nov 2006–May 2019)",
            structural_context="Software Development Manager, Oracle (Nov 2006–May 2019)",
            source_quote="Led Oracle Cloud PaaS services.",
        ),
    ]

    requirement = EvidenceRequirement()

    ranked = ranker.rank(
        question="What did Amod do at 24[7].ai?",
        candidates=candidates,
        evidence_requirement=requirement,
    )

    assert ranked[0].candidate_id == "C2"


def test_ranker_prioritizes_structural_context_when_heading_is_empty():
    """Prioritize structural context when the heading is unavailable."""

    ranker = _ranker()

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="",
            structural_context=(
                "Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)"
            ),
            source_quote="Led AI-powered customer engagement platforms.",
        ),
        _candidate(
            candidate_id="C2",
            heading="Senior Engineering Manager, Cloudera",
            structural_context="Senior Engineering Manager, Cloudera",
            source_quote="Led 25+ engineers across India, US and Europe.",
        ),
    ]

    requirement = EvidenceRequirement()

    ranked = ranker.rank(
        question="What did Amod do at 24[7].ai?",
        candidates=candidates,
        evidence_requirement=requirement,
    )

    assert ranked[0].candidate_id == "C1"


def test_ranker_prioritizes_candidate_with_required_temporal_evidence():
    """Prioritize candidates containing temporal evidence required by the question."""

    ranker = _ranker()

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="Employment",
            structural_context="Employment History",
            source_quote="Worked as an engineering manager for the company.",
        ),
        _candidate(
            candidate_id="C2",
            heading="Employment",
            structural_context="Employment History",
            source_quote="Worked as an engineering manager for 12 years.",
        ),
    ]

    requirement = EvidenceRequirement(
        direct_answer_required=True,
        temporal_value_required=True,
    )

    ranked = ranker.rank(
        question="How long did the person work as an engineering manager?",
        candidates=candidates,
        evidence_requirement=requirement,
    )

    assert ranked[0].candidate_id == "C2"

def test_ranker_prioritizes_candidate_with_required_relationship_evidence():
    """Prioritize candidates containing evidence of a requested relationship."""

    ranker = _ranker()

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="Product",
            structural_context="Product",
            source_quote="The product provides automated reporting.",
        ),
        _candidate(
            candidate_id="C2",
            heading="Product",
            structural_context="Product",
            source_quote=(
                "The product integrates with the customer's existing "
                "identity management system."
            ),
        ),
    ]

    requirement = EvidenceRequirement(
        direct_answer_required=True,
        relationship_required=True,
    )

    ranked = ranker.rank(
        question="How is the product related to the identity management system?",
        candidates=candidates,
        evidence_requirement=requirement,
    )

    assert ranked[0].candidate_id == "C2"

def test_ranker_prioritizes_candidate_with_required_quantity_evidence():
    """Prioritize candidates containing the quantity required by the question."""

    ranker = _ranker()

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="Revenue",
            structural_context="Financial Results > Revenue",
            source_quote="The company generated strong revenue during the year.",
        ),
        _candidate(
            candidate_id="C2",
            heading="Revenue",
            structural_context="Financial Results > Revenue",
            source_quote="The company generated revenue of Rs. 25 lakh during the year.",
        ),
    ]

    requirement = EvidenceRequirement(
        direct_answer_required=True,
        quantity_required=True,
    )

    ranked = ranker.rank(
        question="What was the total revenue?",
        candidates=candidates,
        evidence_requirement=requirement,
    )

    assert ranked[0].candidate_id == "C2"