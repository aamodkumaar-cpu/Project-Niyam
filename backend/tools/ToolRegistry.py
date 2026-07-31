"""
Tool Registry.

Purpose:
    Registers and provides application tools.

Responsibilities:
    - Register tools
    - Return tools by name

Does NOT:
    - Execute tools
    - Route requests
"""

from backend.tools.ComplianceChecklistTool import ComplianceChecklistTool
from backend.tools.KnowledgeSearchTool import KnowledgeSearchTool


class ToolRegistry:
    """Stores all available tools."""

    def __init__(self):

        self.tools = {

            "compliance_checklist":
                ComplianceChecklistTool(),

            "knowledge_search":
                KnowledgeSearchTool()
        }

# -------------- END - init() ------------------------

    def get(
        self,
        name: str
    ):
        """Return a tool."""
        return self.tools[name]