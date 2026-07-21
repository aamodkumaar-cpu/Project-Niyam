"""
Intent Classifier.

Purpose:
    Detects the user's intent.

Responsibilities:
    - Classify user requests

Does NOT:
    - Retrieve documents
    - Call the LLM
"""

from backend.intents.Intent import Intent
from backend.intents.IntentType import IntentType


class IntentClassifier:
    """Classifies user intent."""

    def classify(
        self,
        question: str
    )-> Intent:

        """Classify the user intent."""

        question = question.lower()

        checklist_keywords = [
            "checklist",
            "compliance",
            "register",
            "registration",
            "applicable",
            "required",
            "mandatory"
        ]

        for keyword in checklist_keywords:
            if keyword in question:
                return Intent(
                    type=IntentType.COMPLIANCE_CHECKLIST
                )

        return Intent(
            type=IntentType.QUESTION
        )