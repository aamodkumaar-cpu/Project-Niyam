"""
Keyword Ranking Strategy Tests.

Purpose:
    Verify that semantic distance and keyword relevance are treated
    as independent retrieval signals.

Responsibilities:
    - Verify semantic distance contributes to ranking.
    - Verify keyword-only candidates use keyword relevance.
    - Verify keyword scores are not interpreted as semantic distances.

Does NOT:
    - Test retrieval from ChromaDB.
    - Test document ingestion.
    - Test answer generation.
    - Test API behavior.
"""

from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KeywordRankingStrategy import KeywordRankingStrategy
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode


def _create_node(
    content: str,
    document_id: str,
    semantic_distance: float | None = None,
    keyword_score: float = 0.0,
) -> KnowledgeNode:
    """Create a KnowledgeNode for ranking tests."""

    metadata = DocumentMetadata(
        document_id=document_id,
        source=f"{document_id}.pdf",
        page_number=1,
        chunk_number=1,
        domain=KnowledgeDomain.GENERAL,
        compliance_pack="",
    )

    score = (
        semantic_distance
        if semantic_distance is not None
        else keyword_score
    )

    return KnowledgeNode(
        content=content,
        score=score,
        metadata=metadata,
        semantic_distance=semantic_distance,
        keyword_score=keyword_score,
    )


def _create_ranking_strategy() -> KeywordRankingStrategy:
    """Create a ranking strategy with its production dependencies."""

    return KeywordRankingStrategy(
        keyword_tokenizer=KeywordTokenizer(),
        keyword_scorer=KeywordScorer(),
    )


def test_semantic_distance_is_used_for_semantic_candidates() -> None:
    """Ensure semantic candidates are ranked using semantic distance."""

    strong = _create_node(
        content="Strong semantic match.",
        document_id="strong",
        semantic_distance=0.2,
    )

    weak = _create_node(
        content="Weak semantic match.",
        document_id="weak",
        semantic_distance=0.8,
    )

    ranked = _create_ranking_strategy().rank(
        question="semantic match",
        candidates=[weak, strong],
    )

    assert ranked[0].metadata.document_id == "strong"


def test_keyword_only_candidate_uses_keyword_score() -> None:
    """Ensure keyword-only candidates use their lexical retrieval signal."""

    semantic = _create_node(
        content="General company information.",
        document_id="semantic",
        semantic_distance=0.9,
    )

    keyword = _create_node(
        content="CDK Global billing platform.",
        document_id="keyword",
        keyword_score=3.0,
    )

    ranked = _create_ranking_strategy().rank(
        question="CDK Global billing platform",
        candidates=[semantic, keyword],
    )

    assert any(
        node.metadata.document_id == "keyword"
        for node in ranked
    )


def test_keyword_score_is_not_treated_as_semantic_distance() -> None:
    """Ensure keyword-only nodes have no fabricated semantic relevance."""

    keyword = _create_node(
        content="Specific keyword match.",
        document_id="keyword",
        keyword_score=5.0,
    )

    ranked = _create_ranking_strategy().rank(
        question="specific keyword match",
        candidates=[keyword],
    )

    assert len(ranked) == 1
    assert ranked[0].semantic_distance is None
    assert ranked[0].keyword_score > 0.0
    assert ranked[0].keyword_score <= 1.0

def test_keyword_evidence_beats_unrelated_semantic_candidate() -> None:
    """Ensure lexical evidence prevents unrelated semantic candidates from dominating."""

    cloudera = _create_node(
        content="Cloudera platform modernization and cloud cost reduction.",
        document_id="cloudera",
        semantic_distance=0.9,
    )

    unrelated = _create_node(
        content="Dust storms are caused by strong winds and dry soil.",
        document_id="textbook",
        semantic_distance=0.94,
    )

    ranked = _create_ranking_strategy().rank(
        question="What did Amod accomplish at Cloudera?",
        candidates=[unrelated, cloudera],
    )

    assert ranked[0].metadata.document_id == "cloudera"
