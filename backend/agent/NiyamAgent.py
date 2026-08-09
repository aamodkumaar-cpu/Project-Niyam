"""
Niyam Agent.

Type:
    Agent (Orchestrator)

Purpose:
    Coordinates the complete lifecycle of a user request.

Responsibilities:
    - Detect intent
    - Build execution plans
    - Execute plans
    - Build the final response

Does NOT:
    - Execute individual tools
    - Retrieve knowledge directly
    - Call repositories
"""

from backend.intents.IntentClassifier import IntentClassifier
from backend.memory.ConversationMemory import ConversationMemory
from backend.orchestration.ExecutionExecutor import ExecutionExecutor
from backend.orchestration.ExecutionPlanner import ExecutionPlanner
from backend.orchestration.ExecutionResult import ExecutionResult
from backend.orchestration.RequestContext import RequestContext
from backend.presentation.ResponseBuilder import ResponseBuilder
from backend.results.AnswerResult import AnswerResult


class NiyamAgent:
    """Coordinates the request lifecycle."""

    intent_classifier: IntentClassifier
    request_planner: ExecutionPlanner
    plan_executor: ExecutionExecutor
    response_builder: ResponseBuilder
    conversation_memory: ConversationMemory

    def __init__(
        self,
        intent_classifier: IntentClassifier,
        request_planner: ExecutionPlanner,
        plan_executor: ExecutionExecutor,
        response_builder: ResponseBuilder,
        conversation_memory: ConversationMemory
    ) -> None:
        """Initialize the Niyam agent."""

        self.intent_classifier = intent_classifier
        self.request_planner = request_planner
        self.plan_executor = plan_executor
        self.response_builder = response_builder
        self.conversation_memory = conversation_memory

#------------ END of init() ---------------

    def handle(
        self,
        context: RequestContext
    ) -> ExecutionResult:
        """Handle a request."""

        last_turn = self.conversation_memory.last_turn()

        if last_turn is not None:
            print("\n--- Conversation Memory ---")
            print(f"Previous Question : {last_turn.question}")
            print("---------------------------\n")

        intent = self.intent_classifier.classify(
            context.question
        )

        plan = self.request_planner.create_plan(
            intent
        )

        execution = self.plan_executor.execute(
            plan,
            context
        )

        answer = self.response_builder.build(
            execution.result
        )

        self.conversation_memory.add(
            context.question,
            answer
        )

        execution.answer = answer
        return execution