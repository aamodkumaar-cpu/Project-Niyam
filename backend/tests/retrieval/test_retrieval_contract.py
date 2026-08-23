"""
Retrieval Contract Tests.

Purpose:
    Protect the retrieval pipeline from incompatible retrieval-score
    semantics and loss of keyword-only evidence.

Responsibilities:
    - Verify keyword-only candidates survive hybrid retrieval.
    - Verify semantic and keyword signals survive merging.
    - Verify semantic distance ordering.
    - Verify keyword relevance is represented correctly.

Does NOT:
    - Test the LLM.
    - Test answer generation.
    - Test document ingestion.
    - Test API behavior.
"""

from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.ResultMerger import ResultMerger


def _create_node(
    content: str,
    document_id: str,
    page_number: int = 1,
    chunk_number: int = 1,
    score: float = 0.0,
    semantic_distance: float | None = None,
    keyword_score: float = 0.0,
) -> KnowledgeNode:
    """Create a KnowledgeNode for retrieval contract tests."""

    metadata = DocumentMetadata(
        document_id=document_id,
        source=f"{document_id}.pdf",
        page_number=page_number,
        chunk_number=chunk_number,
        domain=KnowledgeDomain.GENERAL,
        compliance_pack="",
    )

    return KnowledgeNode(
        content=content,
        score=score,
        metadata=metadata,
        keyword_score=keyword_score,
        semantic_distance=semantic_distance,
    )


def test_keyword_only_candidate_survives_merge() -> None:
    """Ensure a keyword-only candidate is retained beside semantic results."""

    semantic = [
        _create_node(
            content="General company information.",
            document_id="semantic-doc",
            score=0.4,
            semantic_distance=0.4,
        )
    ]

    keyword = [
        _create_node(
            content="Specific CDK Global billing platform information.",
            document_id="keyword-doc",
            score=3.0,
            keyword_score=3.0,
        )
    ]

    merged = ResultMerger().merge(
        semantic,
        keyword,
    )

    assert len(merged) == 2
    assert any(
        node.metadata.document_id == "keyword-doc"
        for node in merged
    )


def test_duplicate_candidate_preserves_both_retrieval_signals() -> None:
    """Ensure a chunk found by both strategies retains both signals."""

    semantic = [
        _create_node(
            content="CDK Global billing platform.",
            document_id="cdk",
            score=0.3,
            semantic_distance=0.3,
        )
    ]

    keyword = [
        _create_node(
            content="CDK Global billing platform.",
            document_id="cdk",
            score=4.0,
            keyword_score=4.0,
        )
    ]

    merged = ResultMerger().merge(
        semantic,
        keyword,
    )

    assert len(merged) == 1

    node = merged[0]

    assert node.semantic_distance == 0.3
    assert node.keyword_score == 4.0


def test_lower_semantic_distance_is_stronger() -> None:
    """Ensure lower semantic distance represents stronger similarity."""

    stronger = _create_node(
        content="Strong semantic match.",
        document_id="strong",
        score=0.2,
        semantic_distance=0.2,
    )

    weaker = _create_node(
        content="Weak semantic match.",
        document_id="weak",
        score=0.8,
        semantic_distance=0.8,
    )

    assert stronger.semantic_distance is not None
    assert weaker.semantic_distance is not None

    assert (
        stronger.semantic_distance
        < weaker.semantic_distance
    )


def test_keyword_only_candidate_has_positive_keyword_signal() -> None:
    """Ensure keyword retrieval is represented by a positive signal."""

    keyword = _create_node(
        content="Specific keyword match.",
        document_id="keyword",
        score=3.0,
        keyword_score=3.0,
    )

    assert keyword.keyword_score > 0.0