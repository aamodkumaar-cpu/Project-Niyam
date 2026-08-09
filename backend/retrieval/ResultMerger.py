"""
Result Merger.

Type:
    Retrieval Pipeline Component

Purpose:
    Merges knowledge retrieved from multiple retrieval strategies.

Responsibilities:
    - Merge retrieval results.
    - Remove duplicate knowledge nodes.
    - Preserve retrieval order.

Does NOT:
    - Filter weak results.
    - Rank results.
    - Build prompts.
    - Call the LLM.
"""

from backend.retrieval.KnowledgeNode import KnowledgeNode


class ResultMerger:
    """Merges retrieval results from multiple strategies."""

    def merge(
        self,
        existing_nodes: list[KnowledgeNode],
        new_nodes: list[KnowledgeNode]
    ) -> list[KnowledgeNode]:
        """
        Merge newly retrieved knowledge with existing results.
        """

        merged: list[KnowledgeNode] = []
        seen: set[tuple[str, int]] = set()

        # Preserve existing order first, then append new results.
        for node in [*existing_nodes, *new_nodes]:

            key = (
                node.metadata.document_id,
                node.metadata.chunk_number
            )

            if key in seen:
                continue

            seen.add(key)
            merged.append(node)

        return merged