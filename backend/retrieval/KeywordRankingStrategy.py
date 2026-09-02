"""
Keyword Ranking Strategy.

Type:
    Ranking Strategy

Purpose:
    Re-rank retrieved knowledge nodes using semantic and lexical
    retrieval signals.

Responsibilities:
    - Convert semantic distance into normalized relevance.
    - Calculate keyword relevance for every candidate.
    - Apply the retrieval question-token policy consistently.
    - Combine semantic and keyword signals deterministically.
    - Store the normalized relevance score on each knowledge node.

Does NOT:
    - Retrieve knowledge.
    - Filter candidates.
    - Modify source metadata.
    - Apply document-specific rules.
    - Call the LLM.
"""

from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.RankingStrategy import RankingStrategy


class KeywordRankingStrategy(RankingStrategy):
    """Ranks merged knowledge nodes using semantic and keyword relevance."""

    _KEYWORD_STOP_WORDS: frozenset[str] = frozenset({
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "this",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
        "each",
        "other",
        "associated",
    })

    def __init__(
        self,
        keyword_tokenizer: KeywordTokenizer,
        keyword_scorer: KeywordScorer,
    ) -> None:
        """Initialize the keyword ranking strategy."""

        self.keyword_tokenizer = keyword_tokenizer
        self.keyword_scorer = keyword_scorer

    def rank(
        self,
        question: str,
        candidates: list[KnowledgeNode],
    ) -> list[KnowledgeNode]:
        """Rank all candidates using semantic and keyword signals."""

        question_tokens = self._get_question_tokens(
            question
        )

        scored: list[tuple[float, KnowledgeNode]] = []

        for node in candidates:
            content_tokens = self.keyword_tokenizer.tokenize(
                node.content
            )

            keyword_relevance = self.keyword_scorer.score(
                query_tokens=question_tokens,
                content_tokens=content_tokens,
            )

            semantic_relevance = self._semantic_relevance(
                node.semantic_distance
            )

            node.keyword_score = keyword_relevance

            final_score = self._combine_scores(
                semantic_relevance=semantic_relevance,
                keyword_relevance=keyword_relevance,
            )

            node.score = final_score

            scored.append(
                (
                    final_score,
                    node,
                )
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            node
            for _, node in scored
        ]

    def _get_question_tokens(
        self,
        question: str,
    ) -> list[str]:
        """Return meaningful normalized question tokens."""

        tokens = self.keyword_tokenizer.tokenize(
            question
        )

        return [
            token
            for token in tokens
            if len(token) >= 3
            and token not in self._KEYWORD_STOP_WORDS
        ]

    def _semantic_relevance(
        self,
        distance: float | None,
    ) -> float:
        """Convert semantic distance into normalized relevance."""

        if distance is None:
            return 0.0

        return 1.0 / (
            1.0 + max(distance, 0.0)
        )

    def _combine_scores(
        self,
        semantic_relevance: float,
        keyword_relevance: float,
    ) -> float:
        """Combine semantic and keyword relevance deterministically."""

        return (
            keyword_relevance * 0.7
        ) + (
            semantic_relevance * 0.3
        )