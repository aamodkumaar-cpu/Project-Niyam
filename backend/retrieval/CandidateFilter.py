"""
Candidate Filter.

Type:
    Domain Service

Purpose:
    Removes retrieval candidates that are clearly unrelated to the user's
    question before prompt construction.

Responsibilities:
    - Inspect retrieved knowledge
    - Remove unrelated documents
    - Preserve only relevant candidates

Does NOT:
    - Retrieve knowledge
    - Rank knowledge
    - Build prompts
    - Call the LLM
"""

from backend.retrieval.KnowledgeNode import KnowledgeNode


class CandidateFilter:
    """Filters unrelated retrieval candidates."""

    def filter(
        self,
        question: str,
        candidates: list[KnowledgeNode]
    ) -> list[KnowledgeNode]:
        """Remove obviously unrelated documents."""

        if not candidates:
            return []

        question = question.lower()

        filtered: list[KnowledgeNode] = []

        for node in candidates:

            source = node.metadata.source.lower()

            if self._matches_resume(question):

                if "amod" in source or "resume" in source:
                    filtered.append(node)

                continue

            if self._matches_gst(question):

                if "gst" in source:
                    filtered.append(node)

                continue

            filtered.append(node)

        return filtered if filtered else candidates

    # ---------- Private ----------

    def _matches_resume(
        self,
        question: str
    ) -> bool:
        """Return True when the question is about the resume."""

        keywords = (
            "amod",
            "resume",
            "experience",
            "career",
            "worked",
            "company",
            "companies",
            "employment",
            "job",
            "profile"
        )

        return any(
            keyword in question
            for keyword in keywords
        )

    def _matches_gst(
        self,
        question: str
    ) -> bool:
        """Return True when the question is about GST."""

        keywords = (
            "gst",
            "registration",
            "tax",
            "invoice",
            "input tax",
            "cgst",
            "sgst",
            "igst"
        )

        return any(
            keyword in question
            for keyword in keywords
        )