"""
Result Merger.

Type:
    Domain Service

Purpose:
    Merge retrieval results from multiple retrieval strategies into
    one deterministic ranked result set.

Responsibilities:
    - Merge semantic and keyword retrieval results.
    - Remove duplicate source chunks.
    - Preserve the strongest score for duplicates.
    - Rank results by descending relevance.

Does NOT:
    - Retrieve knowledge.
    - Inspect document semantics.
    - Apply domain-specific rules.
    - Call the LLM.
"""

from backend.retrieval.KnowledgeNode import KnowledgeNode


class ResultMerger:
    """Merges and deterministically ranks retrieval results."""

    def merge(
        self,
        semantic_nodes: list[KnowledgeNode],
        keyword_nodes: list[KnowledgeNode],
    ) -> list[KnowledgeNode]:
        """Merge, deduplicate, and rank retrieval results."""

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

            if node.score > existing.score:
                merged[key] = node

        return sorted(
            merged.values(),
            key=lambda node: node.score,
            reverse=True,
        )

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