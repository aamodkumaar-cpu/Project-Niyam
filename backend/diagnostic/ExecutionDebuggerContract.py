"""
Execution Debugger Contract.

Type:
    Infrastructure Contract

Purpose:
    Define the diagnostic operations required by domain services.

Responsibilities:
    - Define diagnostic contracts used by application services.

Does NOT:
    - Implement logging.
    - Persist diagnostics.
    - Contain business logic.
"""

from __future__ import annotations

from typing import Protocol

from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.llm.Message import Messages
from backend.extraction.KnowledgeFact import KnowledgeFact


class ExecutionDebuggerContract(Protocol):
    """Contract for services that provide execution diagnostics."""

    def prompt(
        self,
        messages: Messages,
    ) -> None:
        """Record the generated prompt."""

    def raw_llm_response(
        self,
        title: str,
        response: str,
    ) -> None:
        """Record the raw LLM response."""

    def extraction(
        self,
        knowledge: StructuredKnowledge,
    ) -> None:
        """Record extracted structured knowledge."""

    def rejected_fact(
        self,
        fact: KnowledgeFact,
    ) -> None:
        """Record a rejected fact."""