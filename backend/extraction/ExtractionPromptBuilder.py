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
    - Instruct the LLM to select candidate IDs only.
    - Explicitly handle exhaustive requests such as "all companies".
    - Explicitly handle maximum-per-heading requests.

Does NOT:
    - Retrieve knowledge.
    - Call the LLM.
    - Validate candidates.
    - Generate source quotes.
    - Generate factual content.
"""

from __future__ import annotations

import re

from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
from backend.llm.Message import Messages


class ExtractionPromptBuilder:
    """Builds candidate-selection prompts."""

    def build(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
    ) -> Messages:
        """Build a prompt that asks the LLM to select candidate IDs only."""

        context = "\n\n".join(
            (
                f"[{candidate.candidate_id}]\n"
                f"Source : {candidate.node.metadata.source}\n"
                f"Page   : {candidate.node.metadata.page_number}\n"
                f"Heading: {candidate.heading}\n"
                f"Fact   : {candidate.source_quote}"
            )
            for candidate in candidates
        )

        maximum = self._extract_maximum_per_heading(
            question
        )

        exhaustive = self._is_exhaustive_request(
            question
        )

        coverage_instruction = self._build_coverage_instruction(
            exhaustive=exhaustive,
            maximum=maximum,
        )

        system_prompt = f"""
You are the knowledge selection component of Project Niyam.

The supplied candidates are the ONLY source of truth.

Your ONLY job is to select candidate IDs whose source facts directly
answer the user question.

You MUST NOT generate factual content.

You MUST NOT write, rewrite, paraphrase, summarize, or modify source text.

You MUST NOT create company names, headings, facts, explanations,
relationships, or source quotes.

The application will resolve selected candidate IDs back to the
original source text.

============================================================
SELECTION RULES
============================================================

1. Return ONLY candidate IDs that exist in the supplied candidates.

2. Select candidates whose FACT directly answers the user question.

3. Do not select candidates merely because they are semantically
   related.

4. Do not infer facts from a candidate heading.

5. Do not combine multiple candidates.

6. Do not rewrite candidate text.

7. Every selected candidate must independently answer the question.

8. Career highlights, certifications, education, and unrelated
   information must not be selected when the question specifically
   asks for company experience.

9. A candidate must remain associated with its supplied heading
   and source.

10. Never invent a candidate ID.

11. If no candidate directly answers the question, return [].

============================================================
EXHAUSTIVE REQUEST HANDLING
============================================================

{coverage_instruction}

============================================================
IMPORTANT
============================================================

For an exhaustive request, DO NOT stop after finding one or two
relevant headings.

First inspect the COMPLETE candidate list.

Identify every heading that represents a relevant company or
professional experience.

Then select the appropriate candidate facts for EACH such heading.

The word "all" means ALL relevant represented headings, not merely
the most relevant headings.

Do not select education, certification, career-highlight, or unrelated
document candidates merely to satisfy the requested count.

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

Select only candidate IDs that directly answer the question.
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

    def _build_coverage_instruction(
        self,
        exhaustive: bool,
        maximum: int | None,
    ) -> str:
        """Build explicit coverage instructions for the request."""

        if not exhaustive:
            if maximum is None:
                return """
This is NOT explicitly an exhaustive request.

Select all candidates that directly answer the question, subject
to the other selection rules.
""".strip()

            return f"""
The question requests a maximum of {maximum} candidate facts per
heading.

Select no more than {maximum} candidates for the same heading.

Do not invent candidates when fewer supported facts exist.
""".strip()

        if maximum is None:
            return """
This is an EXHAUSTIVE request.

The user explicitly asks for ALL relevant companies or experience.

Process the candidates heading-by-heading.

For every heading that explicitly represents a company or professional
experience relevant to the question:

1. Select every candidate that directly answers the question.

2. Do not stop after selecting candidates from the first company.

3. Continue until every relevant company/experience heading in the
   COMPLETE candidate list has been considered.

4. Do not select candidates from unrelated headings.

The final selection must provide coverage across ALL relevant
represented companies.
""".strip()

        return f"""
This is an EXHAUSTIVE request with a maximum of {maximum} facts
per heading.

Process the candidates heading-by-heading.

For EVERY heading that explicitly represents a relevant company or
professional experience:

1. Consider all candidates belonging to that heading.

2. Select up to {maximum} candidates that directly answer the
   question.

3. If the heading has fewer than {maximum} relevant candidates,
   select only the available relevant candidates.

4. Do NOT stop after the first company.

5. Continue until EVERY relevant company/experience heading in the
   COMPLETE candidate list has been considered.

6. Do NOT select unrelated career highlights, certifications,
   education, or unrelated documents.

The final selection must therefore contain coverage from every
relevant represented company, subject to the maximum of
{maximum} candidates per heading.
""".strip()

    def _is_exhaustive_request(
        self,
        question: str,
    ) -> bool:
        """Return whether the question requests exhaustive coverage."""

        normalized = question.lower()

        exhaustive_terms = (
            "all ",
            "all the ",
            "each ",
            "every ",
            "entire ",
            "complete ",
        )

        return any(
            term in normalized
            for term in exhaustive_terms
        )

    def _extract_maximum_per_heading(
        self,
        question: str,
    ) -> int | None:
        """Extract an explicit maximum-per-heading request."""

        match = re.search(
            r"\bmax(?:imum)?\s+(\d+)\b",
            question,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        try:
            maximum = int(
                match.group(1)
            )
        except ValueError:
            return None

        if maximum <= 0:
            return None

        return maximum