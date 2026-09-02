from backend.extraction.EvidenceRequirement import EvidenceRequirement
from backend.extraction.ExtractionQuestionAnalyzer import (
    ExtractionQuestionAnalyzer,
)


def test_analyzer_identifies_required_evidence():
    """Identify evidence characteristics required by a question."""

    analyzer = ExtractionQuestionAnalyzer()

    requirement = analyzer.determine_evidence_requirement(
        "What is Amod Kumar's total engineering experience?"
    )

    assert requirement == EvidenceRequirement(
        direct_answer_required=True,
        quantity_required=True,
        temporal_value_required=True,
    )