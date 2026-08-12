"""
Answer Generator.

Type:
    Domain Service

Purpose:
    Convert structured knowledge into a readable answer.

Responsibilities:
    - Render structured facts as readable bullet points.
    - Group facts by source-owned heading.
    - Keep source information out of individual bullets.
    - Preserve factual wording.

Does NOT:
    - Retrieve knowledge.
    - Generate facts.
    - Modify factual meaning.
    - Validate source grounding.
    - Call the LLM.
"""

from backend.extraction.StructuredKnowledge import (
    StructuredKnowledge,
)


class AnswerGenerator:
    """Generate a readable answer from structured knowledge."""

    def generate(
        self,
        question: str,
        knowledge: StructuredKnowledge,
    ) -> str:
        """Generate the user-facing answer text."""

        _ = question

        if not knowledge.facts:
            return (
                "The supplied knowledge does not contain "
                "the answer."
            )

        lines: list[str] = [
            "The following information was found "
            "in the supplied documents:",
            "",
        ]

        current_name = ""

        for fact in knowledge.facts:

            if fact.name != current_name:
                if current_name:
                    lines.append("")

                lines.append(
                    f"{fact.name}:"
                )

                current_name = fact.name

            display_value = " ".join(
                fact.value.split()
            )

            lines.append(
                f"- {display_value}"
            )

        return "\n".join(
            lines
        )