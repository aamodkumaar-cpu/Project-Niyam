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
from backend.orchestration.RequestContext import RequestContext
from backend.results.AnswerResult import AnswerResult
from backend.tools.ToolRegistry import ToolRegistry
from backend.intents.IntentType import IntentType
from backend.agent.NiyamAgent import NiyamAgent


class RequestRouter:

    def __init__(
        self,
        application: Application
    ):
        """Initialize the request router."""

        self.application = application
        self.agent = NiyamAgent()


    def route(
        self,
        question: str,
        where: dict | None = None
    ) -> AnswerResult:
        """Route the user request."""

        context = RequestContext(
            question=question,
            business_profile=self.application.get_business_profile(),
            where=where
        )

        return self.agent.handle(context)

        # intent = self.application.detect_intent( question )
        # print( f"\nRouting -> {intent.type.name}\n" )

        # if intent.type == IntentType.COMPLIANCE_CHECKLIST:
        #     checklist = checklist = self.tool_registry.get("compliance_checklist").execute( context )
        #     answer = "\n".join( item.title for item in checklist.items )
        #     return AnswerResult(
        #         answer=answer,
        #         sources=[]
        #     )


        # return self.application.search( context)