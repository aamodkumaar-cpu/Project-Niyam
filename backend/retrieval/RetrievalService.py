"""
Retrieval Service.

Type:
    Domain Service

Purpose:
    Coordinates retrieval and ranking strategies.

Responsibilities:
    - Execute retrieval strategies
    - Merge retrieved knowledge
    - Apply ranking strategies
    - Return ranked knowledge nodes

Does NOT:
    - Build prompts
    - Call the LLM
    - Generate embeddings
"""

from collections.abc import Sequence

from chromadb.types import Where

from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.retrieval.RankingStrategy import RankingStrategy
from backend.retrieval.RelevanceFilter import RelevanceFilter
from backend.retrieval.ResultMerger import ResultMerger
from backend.retrieval.RetrievalStrategy import RetrievalStrategy


class RetrievalService:
    """Coordinates retrieval, ranking, and relevance filtering."""

    retrieval_strategies: Sequence[RetrievalStrategy]
    ranking_strategies: Sequence[RankingStrategy]
    result_merger: ResultMerger
    relevance_filter: RelevanceFilter

    def __init__(
        self,
        retrieval_strategies: Sequence[RetrievalStrategy],
        ranking_strategies: Sequence[RankingStrategy],
        result_merger: ResultMerger,
        relevance_filter: RelevanceFilter,
    ) -> None:
        """Initialize retrieval service."""

        self.retrieval_strategies = retrieval_strategies
        self.ranking_strategies = ranking_strategies
        self.result_merger = result_merger
        self.relevance_filter = relevance_filter

    def retrieve(
        self,
        question: str,
        where: Where | None = None,
    ) -> list[KnowledgeNode]:
        """Retrieve, merge, rank, and filter knowledge."""

        retrieved_nodes: list[KnowledgeNode] = []

        # ---------------- Retrieval ----------------

        for strategy in self.retrieval_strategies:
            nodes = strategy.retrieve(
                question=question,
                where=where,
            )

            self._print_nodes(
                strategy.__class__.__name__,
                nodes,
            )

            retrieved_nodes = self.result_merger.merge(
                retrieved_nodes,
                nodes,
            )

        self._print_nodes(
            "MERGED",
            retrieved_nodes,
        )

        # ---------------- Ranking ----------------

        ranked_nodes = list(retrieved_nodes)

        for strategy in self.ranking_strategies:
            ranked_nodes = strategy.rank(
                question=question,
                candidates=ranked_nodes,
            )

        self._print_nodes(
            "RANKED",
            ranked_nodes,
        )

        # ---------------- Relevance Filtering ----------------

        relevant_nodes = self.relevance_filter.filter(
            candidates=ranked_nodes,
        )

        self._print_nodes(
            "RELEVANT",
            relevant_nodes,
        )

        return relevant_nodes

    def _print_nodes(
        self,
        title: str,
        nodes: Sequence[KnowledgeNode],
    ) -> None:
        """Print retrieved knowledge for diagnostics."""

        print(f"\n========== {title} ==========")

        for index, node in enumerate(nodes, start=1):
            print(
                f"{index}. {node.metadata.source} | "
                f"Page {node.metadata.page_number}"
            )