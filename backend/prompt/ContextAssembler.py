"""
Context Assembler.

Type:
    Domain Service

Purpose:
    Converts retrieved knowledge into structured context for downstream LLM prompts.

Responsibilities:
    - Organize retrieved knowledge
    - Build context sections
    - Render readable context
    - Preserve source attribution

Does NOT:
    - Retrieve knowledge
    - Rank knowledge
    - Call the LLM
"""

from collections.abc import Sequence

from backend.prompt.ContextOrganizer import ContextOrganizer
from backend.prompt.ContextSection import ContextSection
from backend.retrieval.KnowledgeNode import KnowledgeNode


class ContextAssembler:
    """Builds structured prompt context."""

    context_organizer: ContextOrganizer

    def __init__(
        self,
        context_organizer: ContextOrganizer
    ) -> None:
        """Initialize the context assembler."""

        self.context_organizer = context_organizer

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def assemble(
        self,
        knowledge_nodes: Sequence[KnowledgeNode]
    ) -> str:
        """Assemble retrieved knowledge into prompt context."""

        organized_nodes = self.context_organizer.organize(
            knowledge_nodes
        )

        sections = self._create_sections(
            organized_nodes
        )

        return self._render(
            sections
        )

    # ---------------------------------------------------------
    # Private
    # ---------------------------------------------------------

    def _create_sections(
        self,
        knowledge_nodes: Sequence[KnowledgeNode]
    ) -> list[ContextSection]:
        """Convert knowledge nodes into context sections."""

        return [
            ContextSection(
                title=(
                    f"{node.metadata.source} "
                    f"(Page {node.metadata.page_number})"
                ),
                content=node.content.strip()
            )
            for node in knowledge_nodes
        ]

    def _render(
        self,
        sections: Sequence[ContextSection]
    ) -> str:
        """Render context sections into prompt text."""

        rendered_sections = [
            "\n".join(
                [
                    f"Source : {section.title}",
                    "",
                    section.content,
                    "-" * 40
                ]
            )
            for section in sections
        ]

        return "\n\n".join(
            rendered_sections
        )