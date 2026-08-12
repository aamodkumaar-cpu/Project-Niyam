"""
Answer Generation Grounding Regression Tests.

Purpose:
    Protect the final answer boundary from hallucination and
    accidental modification of validated knowledge.

Responsibilities:
    - Verify validated facts are rendered.
    - Verify source metadata is preserved.
    - Verify independent facts remain independent.
    - Verify unsupported information cannot appear.
    - Verify question-only information cannot appear.
    - Verify facts are not paraphrased.
    - Verify facts are not combined.
    - Verify empty knowledge produces a safe response.

Does NOT:
    - Retrieve knowledge.
    - Extract knowledge.
    - Call an LLM.
    - Depend on Ollama.
    - Test a specific customer or document.
"""


from backend.extraction.AnswerGenerator import AnswerGenerator
from backend.extraction.KnowledgeFact import KnowledgeFact
from backend.extraction.StructuredKnowledge import StructuredKnowledge


def _create_knowledge(
    facts: list[tuple[str, str, str, int]],
) -> StructuredKnowledge:
    """Create generic validated knowledge for evaluation."""

    knowledge = StructuredKnowledge()

    for name, value, source, page_number in facts:

        knowledge.facts.append(
            KnowledgeFact(
                name=name,
                value=value,
                source=source,
                page_number=page_number,
                confidence=1.0,
            )
        )

    return knowledge


def test_validated_facts_are_rendered() -> None:
    """Ensure validated facts appear in the final answer."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                2,
            ),
            (
                "Company A",
                "Reduced processing time by 40%.",
                "company-a.pdf",
                3,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert "Company A:" in answer

    assert (
        "- Built a billing platform."
        in answer
    )

    assert (
        "- Reduced processing time by 40%."
        in answer
    )


def test_source_information_is_rendered() -> None:
    """Ensure source metadata remains visible in the final answer."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                2,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert (
        "Source: company-a.pdf, Page 2"
        in answer
    )


def test_independent_facts_remain_independent() -> None:
    """Ensure independent facts are not combined."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                1,
            ),
            (
                "Company A",
                "Reduced processing time by 40%.",
                "company-a.pdf",
                2,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert (
        "- Built a billing platform reducing processing time by 40%."
        not in answer
    )

    assert (
        "Built a billing platform. Reduced processing time by 40%."
        not in answer
    )


def test_answer_contains_only_validated_facts() -> None:
    """Ensure unsupported information cannot appear in the answer."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                1,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert (
        "Built a billing platform."
        in answer
    )

    assert (
        "Opened a new international office."
        not in answer
    )

    assert (
        "Reduced processing time by 40%."
        not in answer
    )


def test_source_metadata_remains_attached_to_each_fact() -> None:
    """Ensure each fact keeps its own source and page metadata."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                4,
            ),
            (
                "Company A",
                "Reduced processing time by 40%.",
                "company-b.pdf",
                7,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert (
        "- Built a billing platform.\n"
        "  Source: company-a.pdf, Page 4"
        in answer
    )

    assert (
        "- Reduced processing time by 40%.\n"
        "  Source: company-b.pdf, Page 7"
        in answer
    )


def test_question_information_cannot_become_answer_fact() -> None:
    """Ensure information present only in the question is never rendered."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                1,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question=(
            "What did Company A accomplish after opening "
            "an international office?"
        ),
        knowledge=knowledge,
    )

    assert (
        "Built a billing platform."
        in answer
    )

    assert (
        "international office"
        not in answer
    )


def test_facts_are_not_paraphrased() -> None:
    """Ensure validated fact wording is preserved exactly."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                1,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert (
        "- Built a billing platform."
        in answer
    )

    assert (
        "- Developed a billing system."
        not in answer
    )


def test_facts_are_not_enriched_with_invented_details() -> None:
    """Ensure a validated fact cannot be expanded with invented details."""

    knowledge = _create_knowledge(
        facts=[
            (
                "Company A",
                "Built a billing platform.",
                "company-a.pdf",
                1,
            ),
        ],
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert (
        "- Built a billing platform."
        in answer
    )

    assert (
        "using Kubernetes"
        not in answer
    )

    assert (
        "for international customers"
        not in answer
    )

    assert (
        "reducing costs by 30%"
        not in answer
    )


def test_empty_knowledge_produces_safe_response() -> None:
    """Ensure no answer is fabricated when no facts are available."""

    knowledge = StructuredKnowledge()

    generator = AnswerGenerator()

    answer = generator.generate(
        question="What did Company A accomplish?",
        knowledge=knowledge,
    )

    assert (
        answer
        == "The supplied knowledge does not contain the answer."
    )