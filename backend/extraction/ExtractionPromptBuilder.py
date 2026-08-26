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

Each candidate contains three different types of information:

1. STRUCTURAL CONTEXT:

   Identifies the broader section, scope, role, organization,
   document area, or surrounding context associated with the fact.

2. HEADING:

   Identifies the subject, entity, role, section, or other structural
   label that the fact belongs to.

3. FACT:

   Contains the factual evidence itself.

Use STRUCTURAL CONTEXT and HEADING to determine whether a candidate
belongs to the subject, entity, role, organization, or scope asked
about in the user's question.

The FACT does not need to repeat the entity or subject named in the
question when the HEADING or STRUCTURAL CONTEXT clearly establishes
that relationship.

For questions asking for a ROLE or POSITION, the HEADING itself may
provide the requested answer. In that case, the HEADING is
answer-bearing evidence and the FACT provides supporting evidence
for the candidate's scope.

Example:

Question:
"What was Amod's role at Cloudera?"

Candidate:
Heading: Senior Engineering Manager, Cloudera (Oct 2022–Jun 2025)
Fact: Led 25+ engineers including principal engineers, architects,
and managers across India, US and Europe.

This candidate directly supports the question because the HEADING
explicitly provides Amod's role at Cloudera.

For questions asking what a person DID, ACHIEVED, BUILT, LED, or
DELIVERED, the FACT remains the answer-bearing evidence.

Example:

Question:
"What did Amod do at 24[7].ai?"

Candidate:
Heading: Engineering Manager, 24[7].ai (Mar 2021–Sep 2022)
Fact: Led AI-powered customer engagement platforms.

This candidate directly supports the question because the FACT
provides the requested activity and the HEADING establishes that
the activity belongs to 24[7].ai.

Rules:

1. Return only candidate IDs that exist in the supplied candidates.

2. Select a candidate when its answer-bearing evidence provides the
   information needed to answer the user's question AND its HEADING
   or STRUCTURAL CONTEXT establishes that the evidence belongs to
   the requested subject or scope.

3. For ROLE or POSITION questions, the HEADING may be the
   answer-bearing evidence.

4. For questions asking what a person DID, ACHIEVED, BUILT, LED,
   or DELIVERED, the FACT must provide the answer-bearing evidence.

5. The entity, organization, role, person, date, or other scope from
   the question may be established by the HEADING or STRUCTURAL
   CONTEXT rather than being repeated in the FACT.

6. Different wording is allowed when the meaning is equivalent.

7. Do not use general knowledge.

8. Do not infer or invent facts, relationships, causes, effects,
   organizations, roles, dates, or explanations that are not
   established by the supplied candidate.

9. Do not select a candidate merely because it is semantically
   similar. Its structural context must be compatible with the
   scope of the question.

10. If no candidate provides sufficient evidence within the
    requested scope, return [].

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

Select only the candidate IDs whose answer-bearing evidence directly
supports the user's question and whose heading or structural context
establishes that the evidence belongs to the requested scope.
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
            candidate.structural_context
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
