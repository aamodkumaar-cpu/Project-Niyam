"""
Grounding Regression Tests.

Purpose:
    Protect source fidelity, entity boundaries, ambiguity handling,
    and deterministic candidate selection.
"""

from backend.extraction.ExtractionCandidateBuilder import ExtractionCandidateBuilder
from backend.extraction.ExtractionPromptBuilder import ExtractionPromptBuilder
from backend.extraction.ExtractionResponseParser import ExtractionResponseParser
from backend.extraction.KnowledgeExtractor import KnowledgeExtractor
from backend.extraction.KnowledgeFact import KnowledgeFact
from backend.extraction.KnowledgeSchema import KnowledgeSchema
from backend.extraction.SourceQuoteValidator import SourceQuoteValidator
from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.llm.Message import Messages
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KnowledgeNode import KnowledgeNode


class FakeOllamaService:
    """Returns deterministic LLM responses for grounding tests."""

    def __init__(self, response: str) -> None:
        """Initialize the fake response."""

        self.response = response

    def generate(
        self,
        messages: Messages,
        response_format: object = None,
    ) -> str:
        """Return the configured response."""

        _ = messages
        _ = response_format

        return self.response


class FakeExecutionDebugger:
    """Provides the debugger contract required by KnowledgeExtractor."""

    def prompt(
        self,
        messages: Messages,
    ) -> None:
        """Ignore prompt debugging during tests."""

        _ = messages

    def raw_llm_response(
        self,
        title: str,
        response: str,
    ) -> None:
        """Ignore raw response debugging during tests."""

        _ = title
        _ = response

    def extraction(
        self,
        knowledge: StructuredKnowledge,
    ) -> None:
        """Ignore extraction debugging during tests."""

        _ = knowledge

    def rejected_fact(
        self,
        fact: KnowledgeFact,
    ) -> None:
        """Ignore rejected-fact debugging during tests."""

        _ = fact


def _create_node(
    source: str,
    content: str,
    page_number: int = 1,
) -> KnowledgeNode:
    """Create a generic knowledge node."""

    metadata = DocumentMetadata(
        document_id=source,
        source=source,
        domain=KnowledgeDomain.GENERAL,
        compliance_pack="",
        page_number=page_number,
        chunk_number=0,
    )

    return KnowledgeNode(
        content=content,
        score=1.0,
        metadata=metadata,
    )


def _create_extractor(
    llm_response: str,
) -> KnowledgeExtractor:
    """Create a knowledge extractor with deterministic dependencies."""

    return KnowledgeExtractor(
        prompt_builder=ExtractionPromptBuilder(),
        llm_client=FakeOllamaService(llm_response),
        execution_debugger=FakeExecutionDebugger(),
        knowledge_schema=KnowledgeSchema(),
        source_quote_validator=SourceQuoteValidator(),
        response_parser=ExtractionResponseParser(),
        candidate_builder=ExtractionCandidateBuilder(),
    )


def _response(
    *candidate_ids: str,
) -> str:
    """Build a valid candidate-selection response."""

    items = ",".join(
        f'{{"candidate_id":"{candidate_id}",'
        f'"confidence":1.0}}'
        for candidate_id in candidate_ids
    )

    return f"[{items}]"


def test_atomic_facts_are_separated() -> None:
    """Ensure independently stated facts remain separate candidates."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.\n"
        "● Reduced processing time by 40%.",
    )

    knowledge = _create_extractor(
        _response("C1_1", "C1_2")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[node],
    )

    assert [
        fact.value
        for fact in knowledge.facts
    ] == [
        "Built a billing platform.",
        "Reduced processing time by 40%.",
    ]


def test_facts_cannot_cross_company_boundaries() -> None:
    """Ensure selected evidence keeps its original company attribution."""

    first = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    second = _create_node(
        "Company-B.pdf",
        "Company B\n"
        "● Launched a customer portal.",
    )

    knowledge = _create_extractor(
        _response("C2_1")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[first, second],
    )

    assert len(knowledge.facts) == 1
    assert knowledge.facts[0].name == "Company B"
    assert knowledge.facts[0].source == "Company-B.pdf"


def test_ambiguous_source_attribution_is_rejected() -> None:
    """Reject evidence that exists in multiple source locations."""

    first = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
        1,
    )

    second = _create_node(
        "Company-A-archive.pdf",
        "Company A\n"
        "● Built a billing platform.",
        2,
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[first, second],
    )

    assert knowledge.facts == []


def test_same_document_multiple_pages_are_not_silently_attributed() -> None:
    """Reject evidence repeated on multiple pages of one document."""

    first = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
        1,
    )

    second = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
        2,
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[first, second],
    )

    assert knowledge.facts == []


def test_unique_source_attribution_is_accepted() -> None:
    """Accept a fact represented at one source location."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[node],
    )

    assert len(knowledge.facts) == 1

    assert (
        knowledge.facts[0].value
        == "Built a billing platform."
    )


def test_unsupported_facts_are_rejected() -> None:
    """Reject candidate IDs that do not exist in the source set."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    knowledge = _create_extractor(
        _response("C99_99")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []


def test_paraphrased_fact_is_rejected_by_candidate_contract() -> None:
    """Ensure the LLM has no source-quote field through which it can paraphrase."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    knowledge = _create_extractor(
        '[{"candidate_id":"C1_1",'
        '"source_quote":"Developed a billing system.",'
        '"confidence":1.0}]'
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []


def test_invented_numeric_detail_is_rejected() -> None:
    """Ensure an invented metric cannot enter the source-owned fact."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Reduced processing time by 40%.",
    )

    knowledge = _create_extractor(
        '[{"candidate_id":"C1_1",'
        '"confidence":1.0,'
        '"value":"Reduced processing time by 90%."}]'
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []


def test_invented_causal_relationship_is_rejected() -> None:
    """Ensure causal text cannot be injected through extraction output."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Reduced processing time by 40%.",
    )

    knowledge = _create_extractor(
        '[{"candidate_id":"C1_1",'
        '"confidence":1.0,'
        '"reason":"because of migration"}]'
    ).extract(
        question="Why did Company A improve?",
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []


def test_fact_cannot_be_attributed_to_wrong_entity() -> None:
    """Ensure a selected candidate keeps its own heading."""

    first = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    second = _create_node(
        "Company-B.pdf",
        "Company B\n"
        "● Reduced processing time by 40%.",
    )

    knowledge = _create_extractor(
        _response("C2_1")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[first, second],
    )

    assert knowledge.facts[0].name == "Company B"


def test_real_entity_cannot_receive_invented_achievement() -> None:
    """Ensure a real entity cannot be paired with an invented candidate."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    knowledge = _create_extractor(
        _response("C1_99")
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []


def test_fact_cannot_combine_source_fact_with_invented_continuation() -> None:
    """Ensure extraction output cannot combine source and generated text."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    knowledge = _create_extractor(
        '[{"candidate_id":"C1_1",'
        '"confidence":1.0,'
        '"extra":"and won an award"}]'
    ).extract(
        question="What did Company A accomplish?",
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []


def test_fact_from_one_entity_cannot_use_entity_from_another_document() -> None:
    """Ensure source metadata is owned by the selected candidate."""

    first = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    second = _create_node(
        "Company-B.pdf",
        "Company B\n"
        "● Launched a customer portal.",
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What did Company B accomplish?",
        knowledge_nodes=[first, second],
    )

    assert knowledge.facts[0].source == "Company-A.pdf"
    assert knowledge.facts[0].name == "Company A"


def test_information_present_only_in_question_is_rejected() -> None:
    """Ensure question-only claims cannot become extracted facts."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        "● Built a billing platform.",
    )

    knowledge = _create_extractor(
        _response("C99_1")
    ).extract(
        question=(
            "Company A won an award. "
            "What did Company A accomplish?"
        ),
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []


def test_explicit_maximum_per_heading_is_enforced() -> None:
    """Enforce a user-provided maximum without hardcoding a document type."""

    node = _create_node(
        "Company-A.pdf",
        "Company A\n"
        + "● Fact one.\n"
        + "● Fact two.\n"
        + "● Fact three.",
    )

    knowledge = _create_extractor(
        _response(
            "C1_1",
            "C1_2",
            "C1_3",
        )
    ).extract(
        question=(
            "Share experience. "
            "Share max 2 bullet points from each company."
        ),
        knowledge_nodes=[node],
    )

    assert len(knowledge.facts) == 2

