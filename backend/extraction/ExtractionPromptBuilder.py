"""
Extraction Prompt Builder.

Type:

    Domain Service

Purpose:

    Build a strict candidate-selection prompt for source-grounded
    knowledge extraction.

Responsibilities:

    - Provide the user question.
    - Provide deterministic candidate IDs and source facts.
    - Provide structural context surrounding each candidate.
    - Instruct the LLM to select candidate IDs only.
    - Preserve explicit scope expressed by the user question.

Does NOT:

    - Retrieve knowledge.
    - Call the LLM.
    - Validate candidates.
    - Generate source quotes.
    - Generate factual content.
    - Interpret domain-specific entities.
"""

from __future__ import annotations

from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
from backend.llm.Message import Messages


class ExtractionPromptBuilder:

    """Build strict candidate-selection prompts."""

    def build(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
    ) -> Messages:
        """Build a focused source-grounded candidate-selection prompt."""

        context = "\n\n".join(
            self._format_candidate(candidate)
            for candidate in candidates
        )

        system_prompt = """
    You are the evidence selection component of Project Niyam.

    The supplied candidates are the ONLY source of truth.

    Select the candidate IDs whose FACT directly provides evidence needed
    to answer the user's question.

    Rules:

    1. Return only candidate IDs that exist in the supplied candidates.
    2. Select a candidate only when its FACT directly supports the question.
    3. Different wording is allowed when the meaning is equivalent.
    4. Do not use general knowledge.
    5. Do not infer or invent facts, relationships, causes, effects, or explanations.
    6. If no candidate provides sufficient evidence, return [].

    Return ONLY a JSON array.

    Each selected item must contain exactly:

    {
    "candidate_id": "<candidate ID>",
    "confidence": 1.0
    }

    Do not return explanations, source text, facts, markdown,
    or additional fields.
    """.strip()

        user_prompt = f"""
    USER QUESTION
    =============

    {question}

    CANDIDATES
    ==========

    {context}

    Select only the candidate IDs whose facts directly support
    the user's question.
    """.strip()

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def _format_candidate(
        self,
        candidate: ExtractionCandidate,
    ) -> str:
        """Format one deterministic candidate for the selection prompt."""

        structural_context = (
            " > ".join(
                candidate.structural_context
            )
            if candidate.structural_context
            else "(none explicitly represented)"
        )

        heading = (
            candidate.heading
            if candidate.heading
            else "(none explicitly represented)"
        )

        return (
            f"[{candidate.candidate_id}]\n"
            f"Source : {candidate.node.metadata.source}\n"
            f"Page   : {candidate.node.metadata.page_number}\n"
            f"Structural Context: {structural_context}\n"
            f"Heading: {heading}\n"
            f"Fact   : {candidate.source_quote}"
        )