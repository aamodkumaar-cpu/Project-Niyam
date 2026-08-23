"""
Answer Generator.

Type:
    Domain Service

Purpose:
    Convert structured knowledge into a readable answer.

Responsibilities:
    - Render structured facts as readable bullet points.
    - Group facts by source-owned heading.
    - Preserve source metadata with each fact.
    - Preserve factual wording.

Does NOT:
    - Retrieve knowledge.
    - Generate facts.
    - Modify factual meaning.
    - Validate source grounding.
    - Call the LLM.
"""

from __future__ import annotations

from backend.extraction.AnswerPromptBuilder import AnswerPromptBuilder
from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.llm.Message import Messages
from backend.llm.OllamaService import OllamaService


class AnswerGenerator:
    """
    Generate grounded user-facing answers from structured knowledge.

    Type:
        Domain Service

    Purpose:
        Convert validated StructuredKnowledge into a concise,
        source-grounded answer using the LLM.

    Responsibilities:
        - Build grounded answer-generation prompts.
        - Pass only validated knowledge to the LLM.
        - Generate the final user-facing answer.
        - Return the deterministic fallback when no knowledge exists.

    Does NOT:
        - Retrieve knowledge.
        - Select source candidates.
        - Validate source evidence.
        - Invent facts.
        - Perform independent knowledge discovery.
    """

    def __init__(
        self,
        prompt_builder: AnswerPromptBuilder,
        llm_client: OllamaService,
    ) -> None:
        """Initialize the answer generator."""

        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

    def generate(
        self,
        question: str,
        knowledge: StructuredKnowledge,
    ) -> str:
        """Generate the grounded user-facing answer."""

        if not knowledge.facts:
            return (
                "The supplied knowledge does not contain "
                "the answer."
            )

        messages = self.prompt_builder.build(
            question=question,
            knowledge=knowledge,
        )

        return self.llm_client.generate(
            messages=messages,
        )