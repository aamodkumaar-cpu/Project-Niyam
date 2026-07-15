"""
Result Merger.

Purpose:
    Combines retrieval results from multiple retrieval strategies.

Responsibilities:
    - Merge retrieval results
    - Remove duplicate Knowledge Nodes
    - Preserve ranking

Does NOT:
    - Perform retrieval
    - Generate embeddings
    - Call the LLM
"""

from backend.retrieval.KnowledgeNode import KnowledgeNode


class ResultMerger:

    """Merge retrieval results and remove duplicates."""
    def merge(
        self,
        semantic_nodes: list[KnowledgeNode],
        keyword_nodes: list[KnowledgeNode]
    ) -> list[KnowledgeNode]:

        merged = []
        seen = set()

        for node in semantic_nodes + keyword_nodes:
            key = self._chunk_key(node)
            if key not in seen:
                seen.add(key)
                merged.append(node)
        return merged


    def _chunk_key(
        self,
        node: KnowledgeNode
    ) -> tuple:
        return (
            node.metadata.source,
            node.metadata.page_number,
            node.metadata.chunk_number
        )