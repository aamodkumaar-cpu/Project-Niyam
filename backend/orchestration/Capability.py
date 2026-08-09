"""
Execution Capability.

Purpose:
    Defines the business capabilities that the orchestration engine
    can execute.

Responsibilities:
    - Provide a type-safe identifier for each supported capability.
    - Decouple planning from concrete tool implementations.

Does NOT:
    - Execute any work.
    - Contain business logic.
    - Know which tool implements a capability.
"""

from enum import Enum, auto


class Capability(Enum):
    """
    Business capabilities supported by Project Niyam.
    """

    SEARCH_KNOWLEDGE = auto()
    FORMAT_RESPONSE = auto()
    GENERATE_CHECKLIST = auto()