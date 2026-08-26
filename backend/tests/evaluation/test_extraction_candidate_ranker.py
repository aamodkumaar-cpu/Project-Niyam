from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.extraction.ExtractionCandidateRanker import (
    ExtractionCandidateRanker,
)
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.DocumentMetadata import DocumentMetadata
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
    )


def test_ranker_prioritizes_candidate_whose_heading_matches_question_scope():
    ranker = _ranker()

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="Senior Engineering Manager, Cloudera (Oct 2022–Jun 2025)",
            structural_context=(
                "Senior Engineering Manager, Cloudera (Oct 2022–Jun 2025)"
            ),
            source_quote=(
                "Led 25+ engineers including principal engineers, "
                "architects, and managers across India, US and Europe."
            ),
        ),
        _candidate(
            candidate_id="C2",
            heading="Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)",
            structural_context=(
                "Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)"
            ),
            source_quote=(
                "Led AI-powered customer engagement platforms."
            ),
        ),
        _candidate(
            candidate_id="C3",
            heading="Software Development Manager, Oracle (Nov 2006–May 2019)",
            structural_context=(
                "Software Development Manager, Oracle (Nov 2006–May 2019)"
            ),
            source_quote=(
                "Led Oracle Cloud PaaS services."
            ),
        ),
    ]

    ranked = ranker.rank(
        question="What did Amod do at 24[7].ai?",
        candidates=candidates,
    )

    assert ranked[0].candidate_id == "C2"


def test_ranker_prioritizes_structural_context_when_heading_is_empty():
    ranker = _ranker()

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="",
            structural_context=(
                "Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)"
            ),
            source_quote=(
                "Led AI-powered customer engagement platforms."
            ),
        ),
        _candidate(
            candidate_id="C2",
            heading="Senior Engineering Manager, Cloudera",
            structural_context="Senior Engineering Manager, Cloudera",
            source_quote=(
                "Led 25+ engineers across India, US and Europe."
            ),
        ),
    ]

    ranked = ranker.rank(
        question="What did Amod do at 24[7].ai?",
        candidates=candidates,
    )

    assert ranked[0].candidate_id == "C1"
