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

from typing import Final

from backend.intents.Intent import Intent
from backend.intents.IntentType import IntentType
from backend.retrieval.KeywordTokenizer import KeywordTokenizer


class IntentClassifier:
    """Classifies user intent."""

    tokenizer: KeywordTokenizer

    _CHECKLIST_KEYWORDS: Final[frozenset[str]] = frozenset({
        "checklist",
        "mandatory",
        "required",
        "applicable",
        "compliance",
        "compliances",
        "license",
        "licenses",
        "registration",
        "registrations",
    })

    def __init__(self) -> None:
        self.tokenizer = KeywordTokenizer()


    def classify(
        self,
        question: str
    ) -> Intent:
        """Classify the user intent."""

        words = set(
            self.tokenizer.tokenize(question)
        )

        score = len(
            words.intersection(
                self._CHECKLIST_KEYWORDS
            )
        )

        if score >= 2:
            return Intent(
                type=IntentType.COMPLIANCE_CHECKLIST
            )

        return Intent(
            type=IntentType.QUESTION
        )