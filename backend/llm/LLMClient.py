"""
LLM Client Contract.

Type:
    Infrastructure Contract

Purpose:
    Define the contract required by application services that
    communicate with an LLM.

Responsibilities:
    - Define the LLM generation contract.

Does NOT:
    - Implement LLM communication.
    - Select an LLM provider.
    - Contain business logic.
"""

from __future__ import annotations

from typing import Literal, Protocol

from pydantic.json_schema import JsonSchemaValue

from backend.llm.Message import Messages


class LLMClient(Protocol):
    """Contract for services capable of generating LLM responses."""

    def generate(
        self,
        messages: Messages,
        response_format: (
            JsonSchemaValue
            | Literal["", "json"]
            | None
        ) = None,
    ) -> str:
        """Generate a response from the configured LLM."""
        ...