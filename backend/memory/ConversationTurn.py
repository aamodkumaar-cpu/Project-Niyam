"""
Conversation Turn.

Type:
    Domain Model (DTO)

Purpose:
    Represents one conversation interaction.

Responsibilities:
    - Store the user question
    - Store the generated answer

Does NOT:
    - Execute logic
    - Retrieve knowledge
    - Call the LLM
"""

from dataclasses import dataclass

from backend.results.AnswerResult import AnswerResult


@dataclass
class ConversationTurn:
    """Represents one conversation turn."""

    question: str
    answer: AnswerResult