"""
Tool.

Purpose:
    Represents an executable business capability.

Responsibilities:
    - Execute one business action

Does NOT:
    - Route requests
    - Call other tools
    - Manage conversations
"""


from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Base class for all tools."""

    @abstractmethod
    def execute(
        self,
        context
    ) -> Any:
        """Execute the tool."""
        raise NotImplementedError