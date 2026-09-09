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
    - Identify when structural evidence may be answer-bearing.
    - Enforce complete evaluation for exhaustive questions.

Does NOT:
    - Retrieve knowledge.
    - Call the LLM.
    - Validate candidates.
    - Generate source quotes.
    - Generate factual content.
    - Interpret domain-specific entities.
"""

from __future__ import annotations

from backend.extraction.EvidenceRequirement import EvidenceRequirement
from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.llm.Message import Messages


class ExtractionPromptBuilder:
    """Build strict candidate-selection prompts."""

    def build(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
        evidence_requirement: EvidenceRequirement | None = None,
    ) -> Messages:
        """Build a focused source-grounded candidate-selection prompt."""

        context = "\n\n".join(
            self._format_candidate(candidate)
            for candidate in candidates
        )

        structural_value_required = (
            evidence_requirement.structural_value_required
            if evidence_requirement is not None
            else False
        )

        exhaustive_request = self._is_exhaustive_request(question)

        structural_evidence_instruction = ""

        if structural_value_required:
            structural_evidence_instruction = """
STRUCTURAL VALUE

For this question, STRUCTURAL VALUE is answer-bearing evidence.

The requested answer may be explicitly represented by a candidate's
HEADING or STRUCTURAL CONTEXT rather than by its FACT.

When the HEADING or STRUCTURAL CONTEXT contains the value requested
by the question, select that candidate even when the FACT contains
only supporting information.

Do not require the FACT to repeat the requested value.

Example:

Question:
"What companies did a person work for?"

Candidate:
Heading: Senior Engineering Manager, Example Organization

Fact: Led engineering teams across multiple regions.

The HEADING contains the requested structural value. Therefore,
the candidate may be selected because the structural evidence
identifies the requested value and the FACT provides supporting
evidence for that candidate.

Structural evidence must still be grounded in the supplied
candidate. Do not infer a structural value that is not explicitly
represented in the HEADING or STRUCTURAL CONTEXT.
""".strip()

        exhaustive_instruction = ""

        if exhaustive_request:
            exhaustive_instruction = """
EXHAUSTIVE SELECTION

This question requests a complete set of answers.

You MUST evaluate EVERY supplied candidate independently.

Do not stop after finding several valid candidates.

Do not select only the strongest, highest-scoring, or most obvious
candidates.

For EACH candidate, determine whether its HEADING, STRUCTURAL
CONTEXT, and FACT provide explicit evidence that it answers the
user's question.

Select EVERY candidate that independently satisfies the question.

Do NOT select a candidate merely because it is generally related
to the question.

Do NOT exclude a valid candidate because another candidate appears
stronger or more relevant.

Do NOT assume that the first few candidates are the complete answer.

The ordering of candidates has no meaning.

Completeness applies only to candidates whose evidence directly
supports the user's question. It does NOT mean selecting unrelated
candidates.

Before returning the JSON result, internally evaluate all supplied
candidates against the question.
""".strip()

        system_prompt = f"""
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

{structural_evidence_instruction}

{exhaustive_instruction}

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

5. When STRUCTURAL VALUE is required, the HEADING or STRUCTURAL
   CONTEXT may provide the answer-bearing evidence.

6. The entity, organization, role, person, date, or other scope from
   the question may be established by the HEADING or STRUCTURAL
   CONTEXT rather than being repeated in the FACT.

7. Different wording is allowed when the meaning is equivalent.

8. Do not use general knowledge.

9. Do not infer or invent facts, relationships, causes, effects,
   organizations, roles, dates, or explanations that are not
   established by the supplied candidate.

10. Do not select a candidate merely because it is semantically
    similar. Its structural context must be compatible with the
    scope of the question.

11. For exhaustive questions, completeness is required across the
    supplied candidates. Evaluate every candidate before deciding
    which candidates to return.

12. For exhaustive questions, unrelated candidates must still be
    rejected. Exhaustive does not mean selecting every candidate.

13. If no candidate provides sufficient evidence within the
    requested scope, return [].

Return ONLY a JSON array.

Each selected item must contain exactly:

{{
    "candidate_id": "<candidate ID>",
    "confidence": 1.0
}}

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

Evaluate the supplied candidates against the user's question.

For an exhaustive question, evaluate every supplied candidate and
return every candidate that directly supports the requested answer.

For a non-exhaustive question, return only candidates that directly
support the requested answer.

Select only grounded candidate IDs.
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

    def _is_exhaustive_request(
        self,
        question: str,
    ) -> bool:
        """Detect generic exhaustive wording in the question."""

        return self._contains_exhaustive_term(question)

    def _contains_exhaustive_term(
        self,
        question: str,
    ) -> bool:
        """Return whether the question requests a complete set."""

        normalized = question.lower()

        exhaustive_terms = (
            "all ",
            "each ",
            "every ",
            "list ",
            "enumerate ",
        )

        return any(
            term in normalized
            for term in exhaustive_terms
        )