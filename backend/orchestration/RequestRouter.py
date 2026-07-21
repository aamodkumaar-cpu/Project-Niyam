"""
Request Router.

Purpose:
    Routes user requests to the appropriate business capability.

Responsibilities:
    - Route requests based on intent
    - Invoke the appropriate application service

Does NOT:
    - Retrieve knowledge
    - Build prompts
    - Call the LLM directly
"""

from backend.application import Application
from backend.results.AnswerResult import AnswerResult


class RequestRouter:

    def __init__(
        self,
        application: Application
    ):
        """Initialize the request router."""

        self.application = application

    def route(
        self,
        question: str,
        where: dict | None = None
    ) -> AnswerResult:
        """Route the user request."""

        return self.application.search(
            question=question,
            where=where
        )