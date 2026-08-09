"""
Tool.

Purpose:
    Base abstraction for every executable capability in Project Niyam.

Responsibilities:
    - Expose the business capability implemented by the tool.
    - Execute work using the supplied execution context.

Does NOT:
    - Perform orchestration.
    - Decide when it should execute.
    - Register itself.
"""

from abc import ABC, abstractmethod

from backend.orchestration.ExecutionContext import ExecutionContext
from backend.orchestration.Capability import Capability
from backend.tools.results.ToolResult import ToolResult


class Tool(ABC):
    """
    Base class for all executable tools.
    """

    @property
    @abstractmethod
    def capability(self) -> Capability:
        """
        Business capability implemented by this tool.
        """
        pass

    @abstractmethod
    def execute(
        self,
        context: ExecutionContext
    )-> ToolResult:
        """
        Execute the capability.
        """
        pass