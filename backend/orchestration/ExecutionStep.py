"""
Execution Step.

Type:
    Data Model (DTO)

Purpose:
    Represents one executable step within an execution plan.

Responsibilities:
    - Store the tool to execute
    - Store the tool input
    - Store execution metadata

Does NOT:
    - Execute the tool
    - Perform planning
    - Store business logic
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionStep:
    """Represents one execution step."""
    
    tool_name: str
    input_data: Any = None
    description: str = ""