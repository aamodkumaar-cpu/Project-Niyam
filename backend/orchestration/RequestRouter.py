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

from chromadb.types import Where
from backend.agent.NiyamAgent import NiyamAgent
from backend.compliance.BusinessProfileSession import BusinessProfileSession
from backend.orchestration.ExecutionResult import ExecutionResult
from backend.orchestration.RequestContext import RequestContext


class RequestRouter:
    """Routes user requests to the Niyam agent."""

    business_profile_session: BusinessProfileSession
    agent: NiyamAgent

    def __init__(
        self,
        business_profile_session: BusinessProfileSession,
        agent: NiyamAgent
    ) -> None:
        """Initialize the request router."""

        self.business_profile_session = business_profile_session
        self.agent = agent

#------------ END of init() -------------------

    def route(
        self,
        question: str,
        where: Where | None = None
    ) -> ExecutionResult:
        """
        Route the user request.
        """

        request = RequestContext(
            question=question,
            business_profile=self.business_profile_session.get_business_profile(),
            where=where
        )

        return self.agent.handle(request)