"""
Conversation Memory.

Type:
    Domain Service

Purpose:
    Maintains the conversation history for the current session.

Responsibilities:
    - Store previous questions
    - Store previous answers
    - Return conversation history

Does NOT:
    - Persist data permanently
    - Call the LLM
    - Execute tools
"""

from backend.memory.ConversationTurn import ConversationTurn
from backend.results.AnswerResult import AnswerResult


class ConversationMemory:
    """Stores conversation history."""

    def __init__(self):
        """Initialize memory."""

        self.history: list[ConversationTurn] = []

    def add(
        self,
        question: str,
        answer: AnswerResult
    ) -> None:
        """Store one interaction."""

        self.history.append(
            ConversationTurn(
                question=question,
                answer=answer
            )
        )



    def get_history(
        self
    ) -> list[ConversationTurn]:
        """Return the conversation history."""
        return self.history


    def last_turn(
        self
    ) -> ConversationTurn | None:
        """Return the most recent conversation turn."""
        if not self.history:
            return None

        return self.history[-1]



    def clear(
        self
    ) -> None:
        """Clear the conversation."""

        self.history.clear()