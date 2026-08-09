"""
Answer Generator.

Type:
    Domain Service

Purpose:
    Generate the final user-facing answer from structured knowledge.

Responsibilities:
    - Render validated structured knowledge
    - Preserve factual content exactly

Does NOT:
    - Retrieve knowledge
    - Extract knowledge
    - Call the LLM
    - Invent or modify facts
"""

from backend.extraction.StructuredKnowledge import StructuredKnowledge


class AnswerGenerator:
    """Generates answers from validated structured knowledge."""

    def generate(
        self,
        question: str,
        knowledge: StructuredKnowledge
    ) -> str:
        """Render the validated knowledge as a user-facing answer."""

        if not knowledge.facts:
            return "The supplied knowledge does not contain the answer."

        lines: list[str] = [
            "The following information was found in the supplied documents:",
            ""
        ]

        current_name: str | None = None

        for fact in knowledge.facts:

            if fact.name != current_name:
                if current_name is not None:
                    lines.append("")

                lines.append(
                    f"{fact.name}:"
                )

                current_name = fact.name

            lines.append(
                f"- {fact.value}"
            )

        return "\n".join(lines)