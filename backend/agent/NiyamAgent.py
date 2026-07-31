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
    - Return results

Does NOT:
    - Execute individual tools
    - Retrieve knowledge directly
    - Call repositories
"""


from backend.intents.IntentClassifier import IntentClassifier
from backend.orchestration.ExecutionPlanner import ExecutionPlanner
from backend.orchestration.ExecutionExecutor import ExecutionExecutor
from backend.orchestration.RequestContext import RequestContext
from backend.presentation.ResponseBuilder import ResponseBuilder
from backend.memory.ConversationMemory import ConversationMemory


class NiyamAgent:
    """Coordinates the request lifecycle."""

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.request_planner = ExecutionPlanner()
        self.plan_executor = ExecutionExecutor()
        self.response_builder = ResponseBuilder()
        self.conversation_memory = ConversationMemory()

    
    def handle(
        self,
        context: RequestContext
    ):
        """Handle a request."""
        last_turn = self.conversation_memory.last_turn()
        if last_turn is not None:
            print("\n--- Conversation Memory ---")
            print(f"Previous Question : {last_turn.question}")
            print("---------------------------\n")

        intent = self.intent_classifier.classify( context.question )
        plan = self.request_planner.create_plan( intent )
        execution_result = self.plan_executor.execute(
                            plan,
                            context
                        )
        answer = self.response_builder.build(
                    execution_result.result
                )

        self.conversation_memory.add(
            context.question,
            answer
        )

        return answer