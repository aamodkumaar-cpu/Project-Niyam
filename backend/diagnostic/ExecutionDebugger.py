"""
Execution Debugger.

Type:
    Diagnostic Service

Purpose:
    Displays workflow execution details.

Responsibilities:
    - Display diagnostic information
    - Respect the configured log level

Does NOT:
    - Execute workflows
    - Store execution history
"""

from collections.abc import Sequence
from backend.diagnostic.Logger import Logger
from backend.extraction.KnowledgeFact import KnowledgeFact
from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.llm.Message import Messages
from backend.orchestration.ExecutionTrace import ExecutionTrace
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.ingestion.Chunk import Chunk



class ExecutionDebugger:
    """Displays execution diagnostics."""

    logger: Logger

    def __init__(
        self,
        logger: Logger
    ) -> None:
        """Initialize the debugger."""

        self.logger = logger

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def question(
        self,
        question: str
    ) -> None:
        """Display the current question."""

        self._header("QUESTION")

        self.logger.debug(question)
        self.logger.debug("")


    def retrieval(
        self,
        question: str,
        knowledge_nodes: Sequence[KnowledgeNode]
    ) -> None:
        """Display retrieved knowledge."""

        self._header(
            "RETRIEVED KNOWLEDGE"
        )

        self.logger.debug(
            f"Question : {question}"
        )

        self.logger.debug("")

        if not knowledge_nodes:
            self.logger.debug(
                "No knowledge retrieved."
            )
            self.logger.debug("")
            return

        for index, node in enumerate(
            knowledge_nodes,
            start=1
        ):
            self.logger.debug(
                "-" * 80
            )

            self.logger.debug(
                f"Rank   : {index}"
            )

            self.logger.debug(
                f"Score  : {node.score:.4f}"
            )

            self.logger.debug(
                f"Source : {node.metadata.source}"
            )

            self.logger.debug(
                f"Page   : {node.metadata.page_number}"
            )

            self.logger.debug(
                f"Chunk  : {node.metadata.chunk_number}"
            )

            self.logger.debug("")

            preview = (
                node.content
                .replace("\n", " ")
                .strip()
            )

            if len(preview) > 300:
                preview = preview[:300] + "..."

            self.logger.debug(
                "Preview:"
            )

            self.logger.debug(
                preview
            )

        self.logger.debug("")


    def extraction(
        self,
        knowledge: StructuredKnowledge
    ) -> None:
        """Display extracted knowledge."""

        self._header("STRUCTURED KNOWLEDGE")

        if not knowledge.facts:
            self.logger.debug("No facts extracted.\n")
            return

        for fact in knowledge.facts:

            self.logger.debug(f"Name       : {fact.name}")
            self.logger.debug(f"Value      : {fact.value}")
            self.logger.debug(f"Source     : {fact.source}")
            self.logger.debug(f"Page       : {fact.page_number}")
            self.logger.debug(f"Confidence : {fact.confidence}")
            self.logger.debug("-" * 80)

        self.logger.debug("")


    def answer(
        self,
        answer: str
    ) -> None:
        """Display the generated answer."""

        self._header("FINAL ANSWER")

        self.logger.debug(answer)
        self.logger.debug("")


    def summary(
        self,
        trace: ExecutionTrace
    ) -> None:
        """Display execution summary."""

        self._header("EXECUTION SUMMARY")

        for record in trace.records:

            icon = "✔"

            if record.status.lower() != "success":
                icon = "✘"

            self.logger.debug(
                f"{icon} "
                f"{record.step_name:<35}"
                f"{record.duration:.2f}s"
            )

            if record.message:
                self.logger.debug(
                    f"    {record.message}"
                )

        self.logger.debug("")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _header(
        self,
        title: str
    ) -> None:
        """Display a section header."""

        self.logger.debug("")
        self.logger.debug("=" * 80)
        self.logger.debug(title)
        self.logger.debug("=" * 80)
        self.logger.debug("")

    def raw_llm_response(
        self,
        title: str,
        response: str
    ) -> None:
        """Display the raw response returned by the LLM."""

        self._header(
            f"RAW LLM RESPONSE - {title}"
        )

        self.logger.debug(
            response
        )

        self.logger.debug("")


    def prompt(
        self,
        messages: Messages
    ) -> None:
        """Display the prompt sent to the LLM."""

        self._header("PROMPT")

        for message in messages:

            role = message["role"].upper()

            self.logger.debug(
                f"[{role}]"
            )

            self.logger.debug(
                "-" * 80
            )

            self.logger.debug(
                message["content"]
            )

            self.logger.debug("")




    def chunks(
        self,
        chunks: Sequence[Chunk]
    ) -> None:
        """Display generated chunks."""

        self._header(
            "GENERATED CHUNKS"
        )

        self.logger.debug(
            f"Total Chunks : {len(chunks)}"
        )

        self.logger.debug("")

        for chunk in chunks:

            self.logger.debug(
                "-" * 80
            )

            self.logger.debug(
                f"Chunk  : {chunk.chunk_number}"
            )

            self.logger.debug(
                f"Page   : {chunk.page_number}"
            )

            self.logger.debug(
                f"Length : {len(chunk.text)}"
            )

            preview = (
                chunk.text[:250]
                .replace("\n", " ")
            )

            self.logger.debug("")

            self.logger.debug(
                "Preview:"
            )

            self.logger.debug(
                preview
            )

        self.logger.debug("")


    def rejected_fact(
        self,
        fact: KnowledgeFact
    ) -> None:
        """Display a fact rejected because it was not grounded."""

        self._header("REJECTED FACT")

        self.logger.debug(
            f"Name       : {fact.name}"
        )

        self.logger.debug(
            f"Value      : {fact.value}"
        )

        self.logger.debug(
            f"Source     : {fact.source}"
        )

        self.logger.debug(
            f"Page       : {fact.page_number}"
        )

        self.logger.debug(
            f"Confidence : {fact.confidence}"
        )

        self.logger.debug("")