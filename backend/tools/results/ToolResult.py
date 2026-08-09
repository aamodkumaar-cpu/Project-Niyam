"""
Tool Result.

Purpose:
    Base class for all tool execution results.

Responsibilities:
    - Represent the output produced by a Tool.
    - Provide a common parent type for all tool results.

Does NOT:
    - Execute tools.
    - Perform orchestration.
    - Format responses.
"""


class ToolResult:
    """
    Marker base class for all tool results.

    Every Tool returns a subclass of ToolResult.
    """

    pass