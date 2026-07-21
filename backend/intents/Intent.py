"""
Intent.

Purpose:
    Represents the detected user intent.

Responsibilities:
    - Store detected intent

Does NOT:
    - Classify questions
"""

from dataclasses import dataclass
from backend.intents.IntentType import IntentType


@dataclass
class Intent:
    """Represents a detected intent."""

    type: IntentType