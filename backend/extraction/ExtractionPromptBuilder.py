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
    - Allow complementary source candidates for relationship questions.
    - Handle exhaustive requests.
    - Handle maximum-per-heading requests.

Does NOT:
    - Retrieve knowledge.
    - Call the LLM.
    - Validate candidates.
    - Generate source quotes.
    - Generate factual content.
    - Interpret domain-specific entities.
"""

from __future__ import annotations

import re

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
        """Build a prompt that asks the LLM to select candidate IDs only."""

        context = "\n\n".join(
            self._format_candidate(candidate)
            for candidate in candidates
        )

        maximum = self._extract_maximum_per_heading(
            question
        )

        exhaustive = self._is_exhaustive_request(
            question
        )

        relationship = self._is_relationship_question(
            question
        )

        coverage_instruction = (
            self._build_coverage_instruction(
                exhaustive=exhaustive,
                maximum=maximum,
                relationship=relationship,
            )
        )

        relationship_instruction = (
            """
    For relationship questions, select candidates that provide
    source-grounded evidence for the entities or concepts whose
    relationship is being asked about.

    Do not invent the relationship.

    Select only candidates whose facts provide evidence relevant
    to establishing that relationship.

    If the supplied candidates do not provide sufficient evidence
    for the relationship, return [].
    """
            if relationship
            else
            """
    This is not a relationship question.

    Select candidates according to the general selection rules.
    """
        )

        system_prompt = f"""
    You are the knowledge selection component of Project Niyam.

    The supplied candidates are the ONLY source of truth.

    Your ONLY job is to select candidate IDs that provide source-grounded
    evidence needed to answer the user question.

    You MUST NOT generate factual content.

    You MUST NOT write, rewrite, paraphrase, summarize, or modify source text.

    You MUST NOT create facts, explanations, relationships, or source quotes.

    The application will resolve selected candidate IDs back to the
    original source text.

    ============================================================
    CANDIDATE STRUCTURE
    ============================================================

    Each candidate contains:

    - Candidate ID
    - Source document
    - Source page
    - Structural Context
    - Heading
    - Fact

    Structural Context represents the source document structure surrounding
    the fact.

    Use Structural Context and Heading only to understand the source scope
    in which the fact appears.

    Do NOT invent structural context.

    Do NOT infer a relationship between unrelated structural contexts.

    The Fact remains the authoritative evidence.

    ============================================================
    SELECTION RULES
    ============================================================

    1. Return ONLY candidate IDs that exist in the supplied candidates.

    2. Select candidates that provide evidence needed to answer the user
    question.

    3. Semantic similarity alone is NOT sufficient.

    4. Respect every explicit scope or entity expressed in the question.

    5. If the question explicitly identifies a person, company, vendor,
    product, project, policy, department, location, regulation, or
    other subject, selected candidates must directly belong to that
    requested scope.

    6. Use Structural Context and Heading to determine whether a candidate
    belongs to the requested source scope.

    7. Do NOT select a candidate merely because it concerns the same
    general topic.

    8. Do NOT substitute one entity for another.

    9. Do NOT infer that facts belonging to one entity also belong to
    another entity.

    10. Do NOT use a filename as a substitute for an explicitly represented
        source heading or structural context.

    11. Do NOT infer facts from a heading unless the heading explicitly
        establishes the candidate's scope.

    12. Candidate source, structural context, heading, and fact remain
        inseparable.

    13. Never invent a candidate ID.

    14. If no candidate provides sufficient source-grounded evidence,
        return [].

    ============================================================
    RELATIONSHIP QUESTIONS
    ============================================================

    {relationship_instruction}

    ============================================================
    SCOPE EXAMPLE
    ============================================================

    Question:
    "What did Employee A accomplish at Company X?"

    Candidate:

    Structural Context:
    Company X > Engineering > Platform

    Heading:
    Platform

    Fact:
    Built a distributed platform.

    This candidate may answer the question because its structural context
    places the fact under Company X.

    A candidate with:

    Structural Context:
    Company Y > Engineering > Platform

    must NOT be selected merely because it describes the same type of work.

    The same rule applies to companies, vendors, products, policies,
    projects, employees, regulations, or any other explicitly requested
    entity.

    ============================================================
    EXHAUSTIVE REQUEST HANDLING
    ============================================================

    {coverage_instruction}

    ============================================================
    IMPORTANT
    ============================================================

    For an exhaustive request, inspect the COMPLETE candidate list.

    Do not stop after finding the first relevant candidate or entity.

    For a targeted request, do NOT broaden the answer beyond the explicit
    scope in the question.

    For an exhaustive request, multiple scopes may be valid when the user
    explicitly asks for all/every/each relevant item.

    ============================================================
    OUTPUT
    ============================================================

    Return ONLY valid JSON.

    Return a JSON array.

    Every item MUST contain exactly:

    {{
    "candidate_id": "<existing candidate ID>",
    "confidence": 1.0
    }}

    Do not return:
    - source text
    - facts
    - names
    - headings
    - structural context
    - explanations
    - markdown
    - additional fields
    """

        user_prompt = f"""
    USER QUESTION
    =============

    {question}

    CANDIDATES
    ==========

    {context}

    Select only candidate IDs that provide source-grounded evidence
    needed to answer the question.
    """

        return [
            {
                "role": "system",
                "content": system_prompt.strip(),
            },
            {
                "role": "user",
                "content": user_prompt.strip(),
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



    def _build_coverage_instruction(
        self,
        exhaustive: bool,
        maximum: int | None,
        relationship: bool,
    ) -> str:
        """Build candidate coverage instructions."""

        if relationship:
            return """
        This is a relationship or synthesis request.

        Select candidates that collectively provide source-grounded evidence
        needed to answer the relationship or synthesis question.

        A relationship may require evidence from multiple candidates.

        A candidate does NOT need to independently answer the complete question.

        For example, if the question asks how A and B are associated:

        - select evidence describing A when it is necessary to establish the
        relationship;
        - select evidence describing B when it is necessary to establish the
        relationship;
        - select evidence explicitly connecting A and B when such evidence exists.

        Do NOT require a single candidate to contain both concepts.

        IMPORTANT:
        Selection of complementary evidence does NOT authorize inference,
        speculation, causation, or information that is not supported by the
        selected source candidates.

        The selected candidates must collectively provide sufficient
        source-grounded evidence for the relationship asked by the user.

        Do NOT select unrelated candidates merely because they mention the same
        general topic.

        Do NOT select candidates merely because they contain one of the entities
        mentioned in the question.

        If the candidates do not collectively provide sufficient source-grounded
        evidence to establish the requested relationship, return [].
        """

        if exhaustive:
            if maximum is None:
                return """
        This is an exhaustive request.

        Select all candidates that provide source-grounded evidence needed to
        answer the question.

        Inspect the complete candidate list.
        """

            return f"""
        This is an exhaustive request.

        Select all candidates that provide source-grounded evidence needed to
        answer the question.

        Inspect the complete candidate list.

        Select at most {maximum} candidates per heading.
        """

        if maximum is None:
            return """
        This is a targeted request.

        Select only candidates that provide source-grounded evidence needed to
        answer the question.
        """

        return f"""
        This is a targeted request.

        Select only candidates that provide source-grounded evidence needed to
        answer the question.

        Select at most {maximum} candidates per heading.
        """


    def _is_relationship_question(
        self,
        question: str,
    ) -> bool:
        """Return whether the question asks for a relationship or synthesis."""

        normalized = question.lower()

        relationship_patterns = (
            r"\bhow\s+are\b.+\brelated\b",
            r"\bhow\s+are\b.+\bassociated\b",
            r"\bhow\s+does\b.+\brelate\s+to\b",
            r"\bhow\s+do\b.+\brelate\s+to\b",
            r"\bhow\s+does\b.+\baffect\b",
            r"\brelationship\s+between\b",
            r"\brelation\s+between\b",
            r"\bconnection\s+between\b",
            r"\blink\s+between\b",
            r"\bconnected\b",
        )

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in relationship_patterns
        )




    def _is_exhaustive_request(
        self,
        question: str,
    ) -> bool:
        """Return whether the question requests exhaustive coverage."""

        normalized = question.lower().strip()

        # "each other" describes a relationship between entities.
        # It must never be interpreted as an exhaustive request.
        if re.search(
            r"\beach\s+other\b",
            normalized,
        ):
            return False

        exhaustive_patterns = (
            r"\ball\s+(?:the\s+)?(?:items?|points?|facts?|causes?|"
            r"reasons?|ways?|types?|examples?|factors?)\b",

            r"\beach\s+(?:item|point|fact|cause|reason|way|type|example|factor)\b",

            r"\bevery\s+(?:item|point|fact|cause|reason|way|type|example|factor)\b",

            r"\bfrom\s+all\s+(?:the\s+)?(?:items?|sources?|documents?)\b",

            r"\bfrom\s+each\s+(?:item|source|document)\b",

            r"\bfrom\s+every\s+(?:item|source|document)\b",
        )

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in exhaustive_patterns
        )


    def _extract_maximum_per_heading(
        self,
        question: str,
    ) -> int | None:
        """Extract an explicit maximum-per-heading constraint."""

        patterns = (
            r"\b(?:only|exactly)\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",
            r"\b(?:max(?:imum)?|up\s+to)\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                flags=re.IGNORECASE,
            )

            if match is not None:
                maximum = int(
                    match.group(1)
                )

                if maximum > 0:
                    return maximum

        return None