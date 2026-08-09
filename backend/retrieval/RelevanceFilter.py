"""
Relevance Filter.

Type:
    Domain Service

Purpose:
    Removes obviously irrelevant knowledge nodes before
    prompt construction.

Responsibilities:
    - Inspect retrieved knowledge
    - Remove low-relevance knowledge
    - Return filtered knowledge

Does NOT:
    - Retrieve knowledge
    - Rank knowledge
    - Build prompts
    - Call the LLM
"""

from typing import Final

from backend.retrieval.KnowledgeNode import KnowledgeNode


class RelevanceFilter:
    """Filters retrieved knowledge."""

    _STOP_WORDS: Final[frozenset[str]] = frozenset({
        "the",
        "and",
        "for",
        "with",
        "from",
        "into",
        "this",
        "that",
        "what",
        "when",
        "where",
        "which",
        "who",
        "how",
        "your",
        "their",
        "only",
        "list",
        "show",
        "share",
        "help",
        "give",
        "tell",
        "please",
        "maximum",
        "company",
        "companies",
        "worked",
        "work",
        "all"
    })

    def filter(
        self,
        question: str,
        knowledge_nodes: list[KnowledgeNode]
    ) -> list[KnowledgeNode]:
        """
        Remove obviously irrelevant knowledge.
        """

        if not knowledge_nodes:
            return []

        question_words = {
            word.lower()
            for word in question.split()
            if (
                len(word) >= 3
                and word.lower() not in self._STOP_WORDS
            )
        }

        filtered_nodes: list[KnowledgeNode] = []

        for node in knowledge_nodes:

            content = node.content.lower()

            match_count = sum(
                1
                for word in question_words
                if word in content
            )

            if match_count >= 2:
                filtered_nodes.append(node)

        # Never return an empty list because of
        # aggressive filtering.
        if filtered_nodes:
            return filtered_nodes

        return knowledge_nodes