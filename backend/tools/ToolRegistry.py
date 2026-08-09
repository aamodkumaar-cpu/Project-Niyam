"""
Tool Registry.

Type:
    Infrastructure

Purpose:
    Maintains the mapping between business capabilities and tools.

Responsibilities:
    - Register tools
    - Return tools by capability

Does NOT:
    - Create tools
    - Execute tools
    - Perform orchestration
"""

from backend.orchestration.Capability import Capability
from backend.tools.Tool import Tool


class ToolRegistry:
    """Stores all available tools."""

    _tools: dict[Capability, Tool]

    def __init__(self) -> None:
        """Initialize the registry."""

        self._tools = {}

    # ---------- Public API ----------

    def register(
        self,
        tool: Tool
    ) -> None:
        """Register a tool."""

        self._tools[tool.capability] = tool

    def get(
        self,
        capability: Capability
    ) -> Tool:
        """Return the registered tool."""

        return self._tools[capability]