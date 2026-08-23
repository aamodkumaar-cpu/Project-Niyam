"""
Keyword Retrieval Evidence Tests.

Purpose:
    Verify that keyword retrieval prioritizes meaningful evidence and
    excludes question/activity content from answer evidence.

Responsibilities:
    - Verify question-shaped chunks do not dominate retrieval.
    - Verify meaningful query terms drive keyword retrieval.
    - Verify textbook activity chunks are excluded.

Does NOT:
    - Test semantic retrieval.
    - Test answer generation.
    - Test LLM behavior.
    - Test API behavior.
"""


from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.VectorRepository import VectorRepository


def _metadata() -> DocumentMetadata:
    """Create valid test document metadata."""

    return DocumentMetadata(
        document_id="test-document",
        source="test.pdf",
        domain=KnowledgeDomain.GENERAL,
        compliance_pack="",
        page_number=1,
        chunk_number=1,
    )


def _create_repository() -> VectorRepository:
    """Create a VectorRepository with its production collaborators."""

    return VectorRepository(
        keyword_tokenizer=KeywordTokenizer(),
        keyword_scorer=KeywordScorer(),
    )


def test_keyword_search_does_not_rank_question_chunk_as_answer_evidence(
    monkeypatch,
) -> None:
    """Question-shaped chunks must not dominate keyword retrieval."""

    repository = _create_repository()

    question_chunk = KnowledgeNode(
        content="How are deforestation and erosion associated with each other?",
        score=0.0,
        metadata=_metadata(),
    )

    evidence_chunk = KnowledgeNode(
        content="Erosion removes fertile topsoil and changes the land and soil.",
        score=0.0,
        metadata=_metadata(),
    )

    monkeypatch.setattr(
        repository,
        "get_chunks",
        lambda where=None: [
            question_chunk,
            evidence_chunk,
        ],
    )

    results = repository.keyword_search(
        question="How are deforestation and erosion associated with each other?",
        top_k=2,
    )

    assert results
    assert results[0].content != question_chunk.content


def test_keyword_search_prioritizes_meaningful_query_terms(
    monkeypatch,
) -> None:
    """Meaningful query terms must outweigh common question words."""

    repository = _create_repository()

    unrelated_chunk = KnowledgeNode(
        content="The Earth and the surface are constantly changing.",
        score=0.0,
        metadata=_metadata(),
    )

    deforestation_chunk = KnowledgeNode(
        content=(
            "Human activities such as deforestation disturb "
            "the natural balance of slopes."
        ),
        score=0.0,
        metadata=_metadata(),
    )

    monkeypatch.setattr(
        repository,
        "get_chunks",
        lambda where=None: [
            unrelated_chunk,
            deforestation_chunk,
        ],
    )

    results = repository.keyword_search(
        question=(
            "How are deforestation and erosion "
            "associated with each other?"
        ),
        top_k=2,
    )

    assert results
    assert results[0].content == deforestation_chunk.content


def test_keyword_search_excludes_textbook_activity_chunk(
    monkeypatch,
) -> None:
    """Textbook activity pages must not become answer evidence."""

    repository = _create_repository()

    activity_chunk = KnowledgeNode(
        content=(
            "38 Understanding Society: India and Beyond Grade 9 – Part 1 "
            "6. How are deforestation and erosion associated with each other? "
            "Explain. "
            "7. Develop a plan to protect the land in your local area from erosion. "
            "8. Which disasters do you think you might experience in your region? "
            "Discuss a mitigation plan in your classroom."
        ),
        score=0.0,
        metadata=_metadata(),
    )

    evidence_chunk = KnowledgeNode(
        content=(
            "Human activities such as deforestation disturb the natural "
            "balance of slopes and can increase erosion."
        ),
        score=0.0,
        metadata=_metadata(),
    )

    monkeypatch.setattr(
        repository,
        "get_chunks",
        lambda where=None: [
            activity_chunk,
            evidence_chunk,
        ],
    )

    results = repository.keyword_search(
        question=(
            "How are deforestation and erosion "
            "associated with each other?"
        ),
        top_k=2,
    )

    assert results
    assert all(
        node.content != activity_chunk.content
        for node in results
    )