"""
Grounding Regression Tests.

Purpose:
    Protect source fidelity, entity boundaries, ambiguity handling,
    and deterministic candidate selection.
"""

from backend.extraction.EvidenceSelectionSafetyGate import EvidenceSelectionSafetyGate
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
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode

from backend.extraction.ExtractionCandidateRanker import ExtractionCandidateRanker
from backend.extraction.ExtractionQuestionAnalyzer import ExtractionQuestionAnalyzer
from backend.extraction.EvidenceSignalDetector import EvidenceSignalDetector


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


def test_role_question_uses_candidate_heading_as_answer() -> None:
    """Use the source heading as answer-bearing evidence for role questions."""

    node = _create_node(
        "Amod-Kumar.pdf",
        "Professional Experience\n"
        "Senior Engineering Manager, Cloudera (Oct 2022–Jun 2025)\n"
        "● Led 25+ engineers including principal engineers, "
        "architects, and managers across India, US and Europe.",
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What was Amod's role at Cloudera?",
        knowledge_nodes=[node],
    )

    assert len(knowledge.facts) == 1

    assert (
        knowledge.facts[0].value
        == "Senior Engineering Manager, Cloudera (Oct 2022–Jun 2025)"
    )


def test_did_question_continues_to_use_candidate_fact() -> None:
    """Use the source fact as answer-bearing evidence for activity questions."""

    node = _create_node(
        "Amod-Kumar.pdf",
        "Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)\n"
        "● Led AI-powered customer engagement platforms.",
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What did Amod do at 24[7].ai?",
        knowledge_nodes=[node],
    )

    assert len(knowledge.facts) == 1

    assert (
        knowledge.facts[0].value
        == "Led AI-powered customer engagement platforms."
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


def test_exhaustive_request_covers_all_represented_experience_headings() -> None:
    """Ensure exhaustive requests cover every represented experience heading."""

    cloudera = _create_node(
        "resume.pdf",
        "Senior Engineering Manager, Cloudera (2022–2025)\n"
        "● Built a RAG-based support assistant.\n"
        "● Reduced cluster bootstrap time by 60%.",
    )

    oracle = _create_node(
        "resume.pdf",
        "Software Development Manager, Oracle (2006–2019)\n"
        "● Led Oracle Cloud PaaS services.\n"
        "● Built OCI services.",
    )

    knowledge = _create_extractor(
        _response(
            "C1_1",
            "C1_2",
            "C2_1",
            "C2_2",
        )
    ).extract(
        question=(
            "Share my experience from all companies. "
            "Give me maximum 2 bullet points from each company."
        ),
        knowledge_nodes=[
            cloudera,
            oracle,
        ],
    )

    assert len(knowledge.facts) == 4

    assert [
        fact.name
        for fact in knowledge.facts
    ] == [
        "Senior Engineering Manager, Cloudera (2022–2025)",
        "Senior Engineering Manager, Cloudera (2022–2025)",
        "Software Development Manager, Oracle (2006–2019)",
        "Software Development Manager, Oracle (2006–2019)",
    ]



def test_exhaustive_request_does_not_depend_on_resume_specific_company_names() -> None:
    """Ensure exhaustive selection works with arbitrary professional headings."""

    supplier = _create_node(
        "supplier.pdf",
        "Supplier Operations Lead (2020–2024)\n"
        "● Managed supplier operations.\n"
        "● Improved fulfillment reliability.",
    )

    manufacturer = _create_node(
        "manufacturer.pdf",
        "Manufacturing Director (2018–2023)\n"
        "● Led manufacturing operations.\n"
        "● Reduced production downtime.",
    )

    knowledge = _create_extractor(
        _response(
            "C1_1",
            "C1_2",
            "C2_1",
            "C2_2",
        )
    ).extract(
        question=(
            "Give me experience from all roles. "
            "Give maximum 2 bullet points from each role."
        ),
        knowledge_nodes=[
            supplier,
            manufacturer,
        ],
    )

    assert len(knowledge.facts) == 4

    assert {
        fact.name
        for fact in knowledge.facts
    } == {
        "Supplier Operations Lead (2020–2024)",
        "Manufacturing Director (2018–2023)",
    }



def test_non_exhaustive_general_knowledge_request_is_not_treated_as_experience() -> None:
    """Ensure general knowledge headings are not treated as professional experience."""

    node = _create_node(
        "science.pdf",
        "Climate Change\n"
        "● Climate change can increase extreme weather events.\n"
        "● Rising temperatures affect weather patterns.",
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What does the document say about climate change?",
        knowledge_nodes=[node],
    )

    assert len(knowledge.facts) == 1

    assert (
        knowledge.facts[0].name
        == "Climate Change"
    )

    assert (
        knowledge.facts[0].value
        == "Climate change can increase extreme weather events."
    )

def test_exhaustive_request_completes_missing_experience_heading() -> None:
    """Ensure deterministic completion covers a heading omitted by the LLM."""

    cloudera = _create_node(
        "resume.pdf",
        "Senior Engineering Manager, Cloudera (2022–2025)\n"
        "● Built a RAG-based support assistant.\n"
        "● Reduced cluster bootstrap time by 60%.",
    )

    oracle = _create_node(
        "resume.pdf",
        "Software Development Manager, Oracle (2006–2019)\n"
        "● Led Oracle Cloud PaaS services.\n"
        "● Built OCI services.",
    )

    knowledge = _create_extractor(
        _response("C1_1", "C1_2")
    ).extract(
        question=(
            "Share my experience from all companies. "
            "Give me maximum 2 bullet points from each company."
        ),
        knowledge_nodes=[
            cloudera,
            oracle,
        ],
    )

    assert len(knowledge.facts) == 4

    assert {
        fact.name
        for fact in knowledge.facts
    } == {
        "Senior Engineering Manager, Cloudera (2022–2025)",
        "Software Development Manager, Oracle (2006–2019)",
    }


def test_unsupported_relationship_returns_no_knowledge() -> None:
    """Reject relationships that are not explicitly stated by the source."""

    node = _create_node(
        "iest102.pdf",
        "Human activities, such as deforestation, disturb "
        "the natural balance of slopes. "
        "Erosion removes fertile topsoil needed for crop growth.",
    )

    knowledge = _create_extractor(
        _response()
    ).extract(
        question=(
            "How are deforestation and erosion "
            "associated with each other?"
        ),
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []





def test_supported_relationship_selects_complementary_evidence() -> None:
    """Select complementary source evidence for a supported relationship."""

    node = _create_node(
        "iest102.pdf",
        "Deforestation removes vegetation from the land. "
        "Sparse vegetation leaves the land exposed to erosion.",
    )

    knowledge = _create_extractor(
        _response("C1_1", "C1_2")
    ).extract(
        question=(
            "How are deforestation and erosion "
            "associated with each other?"
        ),
        knowledge_nodes=[node],
    )

    assert len(knowledge.facts) == 2

    assert [
        fact.value
        for fact in knowledge.facts
    ] == [
        "Deforestation removes vegetation from the land.",
        "Sparse vegetation leaves the land exposed to erosion.",
    ]


def test_relationship_requires_collective_source_support() -> None:
    """Reject relationship selection when evidence does not establish the relationship."""

    node = _create_node(
        "iest102.pdf",
        "Deforestation removes vegetation from the land. "
        "Erosion removes fertile topsoil needed for crop growth.",
    )

    knowledge = _create_extractor(
        _response()
    ).extract(
        question=(
            "How are deforestation and erosion "
            "associated with each other?"
        ),
        knowledge_nodes=[node],
    )

    assert knowledge.facts == []



def test_answer_generator_returns_grounded_llm_answer() -> None:
    """Ensure answer generation delegates synthesis to the grounded LLM."""

    from backend.extraction.AnswerGenerator import AnswerGenerator
    from backend.extraction.AnswerPromptBuilder import AnswerPromptBuilder

    class FakeAnswerLlm:
        """Return a deterministic grounded answer."""

        def generate(
            self,
            messages: Messages,
            response_format: object = None,
        ) -> str:
            """Return a deterministic relationship answer."""

            _ = response_format

            prompt = "\n".join(
                message["content"]
                for message in messages
            )

            assert (
                "Deforestation removes vegetation from the land."
                in prompt
            )

            assert (
                "Sparse vegetation leaves the land exposed to erosion."
                in prompt
            )

            return (
                "Deforestation removes vegetation from the land, "
                "leaving the land exposed to erosion."
            )

    knowledge = StructuredKnowledge(
        facts=[
            KnowledgeFact(
                name="Deforestation",
                value="Deforestation removes vegetation from the land.",
                source="iest102.pdf",
                page_number=1,
                confidence=1.0,
            ),
            KnowledgeFact(
                name="Erosion",
                value=(
                    "Sparse vegetation leaves the land exposed to erosion."
                ),
                source="iest102.pdf",
                page_number=1,
                confidence=1.0,
            ),
        ]
    )

    answer_generator = AnswerGenerator(
        prompt_builder=AnswerPromptBuilder(),
        llm_client=FakeAnswerLlm(),
    )

    answer = answer_generator.generate(
        question=(
            "How are deforestation and erosion "
            "associated with each other?"
        ),
        knowledge=knowledge,
    )

    assert (
        answer
        == (
            "Deforestation removes vegetation from the land, "
            "leaving the land exposed to erosion."
        )
    )


def test_answer_generator_does_not_call_llm_without_knowledge() -> None:
    """Ensure empty structured knowledge returns the grounded fallback."""

    from backend.extraction.AnswerGenerator import AnswerGenerator
    from backend.extraction.AnswerPromptBuilder import AnswerPromptBuilder

    class FailingAnswerLlm:
        """Fail the test if the LLM is called without knowledge."""

        def generate(
            self,
            messages: Messages,
            response_format: object = None,
        ) -> str:
            """Reject unexpected LLM invocation."""

            raise AssertionError(
                "LLM must not be called when structured knowledge is empty."
            )

    answer_generator = AnswerGenerator(
        prompt_builder=AnswerPromptBuilder(),
        llm_client=FailingAnswerLlm(),
    )

    answer = answer_generator.generate(
        question="How are deforestation and erosion associated?",
        knowledge=StructuredKnowledge(),
    )

    assert (
        answer
        == "The supplied knowledge does not contain the answer."
    )





def test_relationship_answer_preserves_complementary_evidence() -> None:
    """Ensure relationship answers retain complementary grounded facts."""

    knowledge = StructuredKnowledge(
        facts=[
            KnowledgeFact(
                name="iest102.pdf",
                value="Deforestation removes vegetation from the land.",
                source="iest102.pdf",
                page_number=1,
                confidence=1.0,
            ),
            KnowledgeFact(
                name="iest102.pdf",
                value=(
                    "Sparse vegetation leaves the land exposed to erosion."
                ),
                source="iest102.pdf",
                page_number=1,
                confidence=1.0,
            ),
        ]
    )

    answer = _create_extractor(
        _response()
    )

    _ = answer


def test_knowledge_search_service_returns_grounded_relationship_answer() -> None:
    """Ensure the complete knowledge search workflow preserves grounded relationship evidence."""

    from backend.diagnostic.ExecutionDebugger import ExecutionDebugger
    from backend.retrieval.KnowledgeSearchService import KnowledgeSearchService

    node = _create_node(
        "iest102.pdf",
        "Deforestation removes vegetation from the land. "
        "Sparse vegetation leaves the land exposed to erosion.",
    )

    class FakeRetrievalPipeline:
        """Returns deterministic source evidence."""

        def retrieve(
            self,
            question: str,
            where: object = None,
        ) -> list[KnowledgeNode]:
            """Return the configured knowledge node."""

            _ = question
            _ = where

            return [node]

    class FakeExecutionDebugger:
        """Provides the debugger contract required by the search service."""

        def question(
            self,
            question: str,
        ) -> None:
            """Ignore question debugging."""

            _ = question

        def retrieval(
            self,
            question: str,
            knowledge_nodes: list[KnowledgeNode],
        ) -> None:
            """Ignore retrieval debugging."""

            _ = question
            _ = knowledge_nodes

        def extraction(
            self,
            knowledge: StructuredKnowledge,
        ) -> None:
            """Ignore extraction debugging."""

            _ = knowledge

        def answer(
            self,
            answer: str,
        ) -> None:
            """Ignore answer debugging."""

            _ = answer

    knowledge_extractor = _create_extractor(
        _response("C1_1", "C1_2")
    )

    from backend.extraction.AnswerGenerator import AnswerGenerator
    from backend.extraction.AnswerPromptBuilder import AnswerPromptBuilder

    class FakeAnswerLlm:
        """Return a deterministic grounded answer."""

        def generate(
            self,
            messages: Messages,
            response_format: object = None,
        ) -> str:
            """Return the expected grounded relationship answer."""

            _ = messages
            _ = response_format

            return (
                "Deforestation removes vegetation from the land. "
                "Sparse vegetation leaves the land exposed to erosion."
            )

    answer_generator = AnswerGenerator(
        prompt_builder=AnswerPromptBuilder(),
        llm_client=FakeAnswerLlm(),
    )

    service = KnowledgeSearchService(
        retrieval_pipeline=FakeRetrievalPipeline(),
        knowledge_extractor=knowledge_extractor,
        answer_generator=answer_generator,
        execution_debugger=FakeExecutionDebugger(),
    )

    from backend.agent.ExecutionContext import ExecutionContext
    from backend.agent.Request import Request

    context = ExecutionContext(
        request=Request(
            question=(
                "How are deforestation and erosion "
                "associated with each other?"
            )
        )
    )

    result = service.search(context)

    assert (
        "Deforestation removes vegetation from the land."
        in result.answer
    )

    assert (
        "Sparse vegetation leaves the land exposed to erosion."
        in result.answer
    )

    assert len(result.sources) == 1

    assert result.sources[0].source == "iest102.pdf"




def test_knowledge_search_service_returns_grounded_relationship_answer() -> None:
    """Ensure the complete knowledge search workflow preserves grounded evidence."""

    from backend.compliance.BusinessProfile import BusinessProfile
    from backend.orchestration.ExecutionContext import ExecutionContext
    from backend.orchestration.RequestContext import RequestContext
    from backend.retrieval.KnowledgeSearchService import KnowledgeSearchService

    class FakeRetrievalPipeline:
        """Return deterministic knowledge nodes for integration testing."""

        def retrieve(
            self,
            question: str,
            where: object = None,
        ) -> list[KnowledgeNode]:
            """Return the configured source node."""

            _ = question
            _ = where

            return [
                _create_node(
                    "iest102.pdf",
                    "Deforestation removes vegetation from the land. "
                    "Sparse vegetation leaves the land exposed to erosion.",
                )
            ]

    class FakeExecutionDebugger:
        """Provide the debugger contract required by the search service."""

        def question(
            self,
            question: str,
        ) -> None:
            """Ignore question debugging."""

            _ = question

        def retrieval(
            self,
            question: str,
            knowledge_nodes: list[KnowledgeNode],
        ) -> None:
            """Ignore retrieval debugging."""

            _ = question
            _ = knowledge_nodes

        def extraction(
            self,
            knowledge: StructuredKnowledge,
        ) -> None:
            """Ignore extraction debugging."""

            _ = knowledge

        def answer(
            self,
            answer: str,
        ) -> None:
            """Ignore answer debugging."""

            _ = answer

    class FakeAnswerLlm:
        """Return a deterministic grounded answer."""

        def generate(
            self,
            messages: Messages,
            response_format: object = None,
        ) -> str:
            """Return the grounded relationship answer."""

            _ = messages
            _ = response_format

            return (
                "Deforestation removes vegetation from the land. "
                "Sparse vegetation leaves the land exposed to erosion."
            )

    knowledge_extractor = _create_extractor(
        _response("C1_1", "C1_2")
    )

    from backend.extraction.AnswerGenerator import AnswerGenerator
    from backend.extraction.AnswerPromptBuilder import AnswerPromptBuilder

    answer_generator = AnswerGenerator(
        prompt_builder=AnswerPromptBuilder(),
        llm_client=FakeAnswerLlm(),
    )

    service = KnowledgeSearchService(
        retrieval_pipeline=FakeRetrievalPipeline(),
        knowledge_extractor=knowledge_extractor,
        answer_generator=answer_generator,
        execution_debugger=FakeExecutionDebugger(),
    )

    business_profile = BusinessProfile(
        business_name="Test Business",
        industry="General",
        company_size=10,
        state="Delhi",
    )

    request = RequestContext(
        question=(
            "How are deforestation and erosion "
            "associated with each other?"
        ),
        business_profile=business_profile,
    )

    context = ExecutionContext(
        request=request,
    )

    result = service.search(context)

    assert (
        "Deforestation removes vegetation from the land."
        in result.answer
    )

    assert (
        "Sparse vegetation leaves the land exposed to erosion."
        in result.answer
    )

    assert len(result.sources) == 1

    assert result.sources[0].source == "iest102.pdf"



def test_supported_semantic_fact_selects_source_evidence() -> None:
    """Ensure semantically equivalent wording can select source evidence."""

    node = _create_node(
        "iest102.pdf",
        "Sparse vegetation cover, often due to deforestation, "
        "also leaves the land exposed.",
    )

    knowledge = _create_extractor(
        _response("C1_1")
    ).extract(
        question="What does deforestation remove from the land?",
        knowledge_nodes=[node],
    )

    assert len(knowledge.facts) == 1

    assert (
        knowledge.facts[0].value
        == (
            "Sparse vegetation cover, often due to deforestation, "
            "also leaves the land exposed."
        )
    )

def test_question_analyzer_identifies_role_question():
    analyzer = ExtractionQuestionAnalyzer()

    assert analyzer.is_role_question(
        "What was Amod's role at Cloudera?"
    )


def test_question_analyzer_does_not_identify_do_question_as_role_question():
    analyzer = ExtractionQuestionAnalyzer()

    assert not analyzer.is_role_question(
        "What did Amod do at Cloudera?"
    )
