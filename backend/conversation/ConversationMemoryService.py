"""
Conversation Memory Service.

Type:
    Domain Service

Purpose:
    Maintains conversational state across user interactions.

Responsibilities:
    - Remember the previous question
    - Remember the previous answer
    - Provide access to stored conversation
    - Clear conversation memory

Does NOT:
    - Retrieve knowledge
    - Build prompts
    - Call the LLM
    - Execute workflows
"""

from typing import Final


class ConversationMemoryService:
    """Stores conversational memory."""

    EMPTY: Final[str] = ""

    _previous_question: str
    _previous_answer: str

    def __init__(
        self
    ) -> None:
        """Initialize empty conversation memory."""

        self.clear()

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def remember_question(
        self,
        question: str
    ) -> None:
        """Store the latest user question."""

        self._previous_question = question

    def remember_answer(
        self,
        answer: str
    ) -> None:
        """Store the latest assistant answer."""

        self._previous_answer = answer

    def previous_question(
        self
    ) -> str:
        """Return the previous user question."""

        return self._previous_question

    def previous_answer(
        self
    ) -> str:
        """Return the previous assistant answer."""

        return self._previous_answer

    def has_previous_question(
        self
    ) -> bool:
        """Return True when a previous question exists."""

        return self._previous_question != self.EMPTY

    def has_previous_answer(
        self
    ) -> bool:
        """Return True when a previous answer exists."""

        return self._previous_answer != self.EMPTY

    def clear(
        self
    ) -> None:
        """Clear all stored conversation."""

        self._previous_question = self.EMPTY
        self._previous_answer = self.EMPTY