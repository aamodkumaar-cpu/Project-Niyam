"""
Context Organizer.

Type:
    Domain Service

Purpose:
    Organizes retrieved knowledge before prompt construction.

Responsibilities:
    - Group chunks by source document
    - Sort pages
    - Sort chunks within each page

Does NOT:
    - Retrieve knowledge
    - Rank knowledge
    - Format prompts
    - Call the LLM
"""

from collections import defaultdict
from collections.abc import Sequence

from backend.retrieval.KnowledgeNode import KnowledgeNode


class ContextOrganizer:
    """Organizes retrieved knowledge."""

    def organize(
        self,
        knowledge_nodes: Sequence[KnowledgeNode]
    ) -> list[KnowledgeNode]:
        """Return knowledge ordered by document, page and chunk."""

        grouped: dict[str, list[KnowledgeNode]] = defaultdict(list)

        for node in knowledge_nodes:
            grouped[node.metadata.source].append(node)

        ordered_nodes: list[KnowledgeNode] = []

        for source in sorted(grouped.keys()):

            ordered_nodes.extend(
                sorted(
                    grouped[source],
                    key=lambda node: (
                        node.metadata.page_number,
                        node.metadata.chunk_number
                    )
                )
            )

        return ordered_nodes