"""
Result Merger.

Type:
    Domain Service

Purpose:
    Merge retrieval results from multiple retrieval strategies into
    one deterministic result set while preserving independent
    retrieval signals.

Responsibilities:
    - Merge semantic and keyword retrieval results.
    - Remove duplicate source chunks.
    - Preserve the strongest semantic signal.
    - Preserve the strongest keyword signal.

Does NOT:
    - Retrieve knowledge.
    - Perform final ranking.
    - Inspect document semantics.
    - Apply domain-specific rules.
    - Call the LLM.
"""

from backend.retrieval.KnowledgeNode import KnowledgeNode


class ResultMerger:
    """Merges retrieval results while preserving retrieval signals."""

    def merge(
        self,
        semantic_nodes: list[KnowledgeNode],
        keyword_nodes: list[KnowledgeNode],
    ) -> list[KnowledgeNode]:
        """Merge semantic and keyword retrieval results."""

        merged: dict[
            tuple[str, int, int],
            KnowledgeNode,
        ] = {}

        for node in [
            *semantic_nodes,
            *keyword_nodes,
        ]:
            key = self._source_key(node)

            existing = merged.get(key)

            if existing is None:
                merged[key] = node
                continue

            merged[key] = self._merge_nodes(
                existing,
                node,
            )

        return list(merged.values())

    def _merge_nodes(
        self,
        first: KnowledgeNode,
        second: KnowledgeNode,
    ) -> KnowledgeNode:
        """Combine retrieval signals from duplicate chunks."""

        semantic_distance = self._best_semantic_distance(
            first.semantic_distance,
            second.semantic_distance,
        )

        keyword_score = max(
            first.keyword_score,
            second.keyword_score,
        )

        if semantic_distance is not None:
            score = semantic_distance
        else:
            score = keyword_score

        return KnowledgeNode(
            content=first.content,
            score=score,
            semantic_distance=semantic_distance,
            keyword_score=keyword_score,
            metadata=first.metadata,
        )

    def _best_semantic_distance(
        self,
        first: float | None,
        second: float | None,
    ) -> float | None:
        """Return the lowest available semantic distance."""

        distances = [
            distance
            for distance in (first, second)
            if distance is not None
        ]

        if not distances:
            return None

        return min(distances)

    def _source_key(
        self,
        node: KnowledgeNode,
    ) -> tuple[str, int, int]:
        """Return the stable identity of a retrieved chunk."""

        return (
            node.metadata.document_id,
            node.metadata.page_number,
            node.metadata.chunk_number,
        )