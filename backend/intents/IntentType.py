"""
Intent Type.

Purpose:
    Defines supported user intents.

Responsibilities:
    - Enumerate supported intents

Does NOT:
    - Classify user queries
"""

from enum import Enum


class IntentType(Enum):

    QUESTION = "QUESTION"

    COMPLIANCE_CHECKLIST = "COMPLIANCE_CHECKLIST"

    UNKNOWN = "UNKNOWN"