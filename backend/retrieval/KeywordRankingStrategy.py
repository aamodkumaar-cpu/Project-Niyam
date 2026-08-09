"""
Keyword Ranking Strategy.

Type:
    Ranking Strategy

Purpose:
    Re-ranks retrieved knowledge nodes using keyword relevance.
"""

from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.RankingStrategy import RankingStrategy


class KeywordRankingStrategy(RankingStrategy):
    """Ranks knowledge nodes using keyword relevance."""

    tokenizer: KeywordTokenizer

    def __init__(self) -> None:
        self.tokenizer = KeywordTokenizer()

    def rank(
        self,
        question: str,
        candidates: list[KnowledgeNode]
    ) -> list[KnowledgeNode]:

        keywords = [
            keyword
            for keyword in self.tokenizer.tokenize(question)
            if len(keyword) >= 2
        ]

        scored: list[tuple[float, KnowledgeNode]] = []

        for node in candidates:

            keyword_score = self._score(
                keywords,
                node
            )

            semantic_score = 1.0 - node.score

            final_score = (
                semantic_score * 1000
            ) + keyword_score

            scored.append(
                (
                    final_score,
                    node
                )
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            node
            for _, node in scored
        ]




    def _score(
        self,
        keywords: list[str],
        node: KnowledgeNode
    ) -> int:

        content = node.content.lower()

        coverage = 0
        frequency = 0

        for keyword in keywords:

            count = content.count(keyword)

            if count > 0:
                coverage += 1
                frequency += count

        score = coverage * 100
        score += frequency * 10

        phrase = " ".join(keywords)

        if phrase and phrase in content:
            score += 200

        return score