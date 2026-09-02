from backend.extraction.EvidenceSelectionSafetyGate import EvidenceSelectionSafetyGate
from backend.extraction.ExtractionCandidateBuilder import (
    ExtractionCandidateBuilder,
)
from backend.extraction.ExtractionCandidateRanker import (
    ExtractionCandidateRanker,
)
from backend.extraction.ExtractionQuestionAnalyzer import (
    ExtractionQuestionAnalyzer,
)
from backend.extraction.ExtractionResponseParser import (
    ExtractionResponseParser,
)
from backend.extraction.KnowledgeExtractor import (
    KnowledgeExtractor,
)
from backend.extraction.KnowledgeSchema import KnowledgeSchema
from backend.extraction.SourceQuoteValidator import (
    SourceQuoteValidator,
)
from backend.extraction.EvidenceSignalDetector import (
    EvidenceSignalDetector,
)
from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.ingestion.KnowledgeDomain import KnowledgeDomain


class FakeLLMClient:
    """Return a deterministic candidate selection."""

    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, messages):
        """Return the configured deterministic response."""

        return self.response


class FakeDebugger:
    """Provide the debugger contract required by the extractor."""

    def prompt(self, messages):
        """Accept prompt diagnostics."""

    def raw_llm_response(self, title, response):
        """Accept raw LLM diagnostics."""

    def extraction(self, knowledge):
        """Accept extraction diagnostics."""

    def rejected_fact(self, fact):
        """Accept rejected-fact diagnostics."""


class FakePromptBuilder:
    """Build a minimal prompt for the fake LLM."""

    def build(self, question, candidates):
        """Return the extraction messages."""

        return [
            {
                "role": "user",
                "content": question,
            }
        ]


def _node(
    content: str,
    page_number: int = 1,
) -> KnowledgeNode:
    """Create a deterministic knowledge node."""

    return KnowledgeNode(
        content=content,
        score=1.0,
        metadata=DocumentMetadata(
            document_id="test-document",
            source="test.pdf",
            domain=KnowledgeDomain.GENERAL,
            compliance_pack="",
            page_number=page_number,
            chunk_number=1,
        ),
    )


def _extractor(
    llm_response: str,
) -> KnowledgeExtractor:
    """Create the production knowledge extractor."""

    return KnowledgeExtractor(
        prompt_builder=FakePromptBuilder(),
        llm_client=FakeLLMClient(llm_response),
        execution_debugger=FakeDebugger(),
        knowledge_schema=KnowledgeSchema(),
        source_quote_validator=SourceQuoteValidator(),
        response_parser=ExtractionResponseParser(),
        candidate_builder=ExtractionCandidateBuilder(),
        question_analyzer=ExtractionQuestionAnalyzer(),
        candidate_ranker=ExtractionCandidateRanker(
            keyword_tokenizer=KeywordTokenizer(),
            keyword_scorer=KeywordScorer(),
            evidence_signal_detector=EvidenceSignalDetector(),
        ),
        evidence_selection_safety_gate=EvidenceSelectionSafetyGate(
            keyword_tokenizer=KeywordTokenizer(),
        ),
    )


def test_knowledge_extractor_returns_only_llm_selected_source_fact():
    """Return only the source fact selected by the extraction pipeline."""

    nodes = [
        _node(
            "The company generated strong revenue during the year."
        ),
        _node(
            "The company generated revenue of Rs. 25 lakh during the year."
        ),
    ]

    extractor = _extractor(
        '[{"candidate_id": "C2_1", "confidence": 1.0}]'
    )

    knowledge = extractor.extract(
        question="What was the total revenue?",
        knowledge_nodes=nodes,
    )

    assert len(knowledge.facts) == 1
    assert knowledge.facts[0].value == (
        "The company generated revenue of Rs. 25 lakh during the year."
    )