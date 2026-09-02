from backend.extraction.EvidenceSelectionSafetyGate import (
    EvidenceSelectionSafetyGate,
)
from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
from backend.retrieval.KeywordTokenizer import KeywordTokenizer


def _candidate(
    candidate_id: str,
    heading: str,
    structural_context: str,
) -> ExtractionCandidate:
    """Build a candidate for safety-gate tests."""

    return ExtractionCandidate(
        candidate_id=candidate_id,
        heading=heading,
        structural_context=structural_context,
        source_quote="Supported factual evidence.",
        node=None,
    )


def test_allows_candidate_matching_explicit_scope() -> None:
    """Allow candidates whose structural evidence matches the requested scope."""

    gate = EvidenceSelectionSafetyGate(
        keyword_tokenizer=KeywordTokenizer(),
    )

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="24[7].ai",
            structural_context="Professional Experience",
        ),
        _candidate(
            candidate_id="C2",
            heading="Cloudera",
            structural_context="Professional Experience",
        ),
    ]

    result = gate.filter(
        question="What did Amod do at 24[7].ai?",
        candidates=candidates,
    )

    assert [candidate.candidate_id for candidate in result] == [
        "C1"
    ]


def test_rejects_candidate_with_conflicting_explicit_scope() -> None:
    """Reject candidates whose structural scope conflicts with the question."""

    gate = EvidenceSelectionSafetyGate(
        keyword_tokenizer=KeywordTokenizer(),
    )

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="Cloudera",
            structural_context="Professional Experience",
        ),
        _candidate(
            candidate_id="C2",
            heading="24[7].ai",
            structural_context="Professional Experience",
        ),
    ]

    result = gate.filter(
        question="What did Amod do at 24[7].ai?",
        candidates=candidates,
    )

    assert [candidate.candidate_id for candidate in result] == [
        "C2"
    ]


def test_preserves_candidates_when_question_has_no_explicit_scope() -> None:
    """Preserve candidates when the question does not establish explicit scope."""

    gate = EvidenceSelectionSafetyGate(
        keyword_tokenizer=KeywordTokenizer(),
    )

    candidates = [
        _candidate(
            candidate_id="C1",
            heading="Cloudera",
            structural_context="Professional Experience",
        ),
        _candidate(
            candidate_id="C2",
            heading="24[7].ai",
            structural_context="Professional Experience",
        ),
    ]

    result = gate.filter(
        question="What programming languages does Amod know?",
        candidates=candidates,
    )

    assert [candidate.candidate_id for candidate in result] == [
        "C1",
        "C2",
    ]