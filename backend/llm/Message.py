"""
LLM Message.

Type:
    Domain Model

Purpose:
    Represents one message exchanged with a chat-based LLM.

Responsibilities:
    - Define the structure of a chat message
    - Provide a reusable message collection type

Does NOT:
    - Call the LLM
    - Build prompts
    - Parse responses
"""

from typing import Literal, TypedDict, TypeAlias


class Message(TypedDict):
    """One LLM chat message."""

    role: Literal["system", "user", "assistant"]

    content: str


Messages: TypeAlias = list[Message]