"""
Prompt Builder.

Type:
    Domain Service

Purpose:
    Builds chat messages for the language model.

Responsibilities:
    - Build the system message
    - Build the user message
    - Combine question and retrieved context
    - Return chat messages

Does NOT:
    - Retrieve knowledge
    - Assemble context
    - Call the LLM
"""

from backend.llm.Message import Messages
from backend.prompt.ContextAssembler import ContextAssembler
from backend.retrieval.KnowledgeNode import KnowledgeNode


SYSTEM_PROMPT = """
You are Project Niyam.

Use ONLY the supplied context.

Answer ONLY with facts explicitly stated in the supplied context.

You MAY:
- Group related facts.
- Present information as bullets, tables or summaries.
- Reorder facts to improve readability.
- Merge information from multiple retrieved sections when they describe the same subject.

You MUST NOT:
- Invent facts.
- Infer missing information.
- Recommend actions unless explicitly stated.
- Use external knowledge.

If the supplied context does not contain the answer,
say that the supplied context does not contain the answer.
""".strip()


class PromptBuilder:
    """Builds chat messages for the language model."""

    context_assembler: ContextAssembler

    def __init__(
        self,
        context_assembler: ContextAssembler
    ) -> None:
        """Initialize the prompt builder."""

        self.context_assembler = context_assembler

    def build(
        self,
        question: str,
        knowledge_nodes: list[KnowledgeNode]
    ) -> Messages:
        """Build chat messages."""

        context = self.context_assembler.assemble(
            knowledge_nodes
        )

        user_message = "\n".join(
            [
                "Question",
                "========",
                question,
                "",
                "Retrieved Context",
                "=================",
                context,
            ]
        )

        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]