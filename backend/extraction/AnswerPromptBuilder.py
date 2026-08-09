"""
Answer Prompt Builder.

Type:
    Domain Service

Purpose:
    Builds prompts for generating answers from structured knowledge.

Responsibilities:
    - Build the system prompt
    - Build the user prompt
    - Convert StructuredKnowledge into LLM messages

Does NOT:
    - Call the LLM
    - Retrieve knowledge
    - Extract facts
"""

from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.llm.Message import Message, Messages


class AnswerPromptBuilder:
    """Builds prompts for grounded answer generation."""

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def build(
        self,
        question: str,
        knowledge: StructuredKnowledge
    ) -> Messages:
        """Build strictly grounded answer generation messages."""

        return [
            Message(
                role="system",
                content=self._system_prompt()
            ),
            Message(
                role="user",
                content=self._user_prompt(
                    question=question,
                    knowledge=knowledge
                )
            )
        ]

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _system_prompt(self) -> str:
        """Return strict grounded answer generation instructions."""

        return """
You are Project Niyam.

Your task is to answer the user's question using ONLY the supplied
Structured Knowledge.

The Structured Knowledge is the ONLY source of truth.

GROUNDING RULES
===============

1. Use ONLY facts explicitly present in Structured Knowledge.

2. NEVER invent a fact.

3. NEVER infer a fact.

4. NEVER assume a fact.

5. NEVER add information from general knowledge.

6. NEVER add information from the user's question as factual
   information.

7. NEVER transfer a fact between companies, roles, people, projects,
   or categories.

8. NEVER change the meaning of a fact.

9. NEVER change a number, percentage, date, name, role, company,
   technology, achievement, or outcome.

10. NEVER convert one type of metric into another.

    Example:

    "30% cloud cost reduction"

    MUST NOT become:

    "30% efficiency improvement."

11. NEVER add a reason, cause, consequence, benefit, or interpretation
    that is not explicitly present in the supplied knowledge.

12. NEVER expand a fact with plausible but unstated details.

13. NEVER combine multiple facts to create a new factual claim.

14. You MAY group facts under their existing company or role heading,
    but grouping MUST NOT change their meaning.

15. Preserve factual wording as closely as possible.

16. If the user requests a specific number of points and fewer supported
    facts are available, return ONLY the supported facts.

17. NEVER invent additional points to satisfy the requested number.

18. If no supported fact answers the question, reply exactly:

The supplied knowledge does not contain the answer.

COMPANY AND ROLE RULES
======================

If facts belong to different companies or roles, keep them separate.

Do not create a new company, role, category, or heading.

EARLY CAREER RULE
=================

If multiple companies are named in an Early Career section but the
supplied knowledge does not associate individual facts with those
companies, do not assign the shared facts to individual companies.

ANSWER RULES
============

Answer only what is supported.

Do not provide commentary about what you think is likely.

Do not provide recommendations unless they are explicitly supported
by the supplied knowledge.

Do not fill missing information.

Accuracy is more important than completeness.

A shorter supported answer is ALWAYS preferable to a longer answer
containing unsupported information.

Return only the final user-facing answer.
""".strip()

    def _user_prompt(
        self,
        question: str,
        knowledge: StructuredKnowledge
    ) -> str:
        """Build the grounded answer user prompt."""

        facts = "\n".join(
            (
                f"Fact {index}:\n"
                f"Company/Role: {fact.name}\n"
                f"Value: {fact.value}\n"
                f"Source: {fact.source}\n"
                f"Page: {fact.page_number}"
            )
            for index, fact in enumerate(
                knowledge.facts,
                start=1
            )
        )

        if not facts:
            facts = "No supported facts are available."

        return f"""
USER QUESTION
=============

{question}

STRUCTURED KNOWLEDGE
====================

{facts}

FINAL INSTRUCTION
=================

Answer the user question using ONLY the facts above.

Every factual statement in your answer must be directly supported
by one or more supplied facts.

Do not add anything that is not explicitly supported.

If the requested information is missing, do not guess.
""".strip()