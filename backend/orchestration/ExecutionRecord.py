"""
Execution Record.

Type:
    Data Model

Purpose:
    Represents one executed workflow step.

Responsibilities:
    - Store execution details

Does NOT:
    - Execute anything
"""


from dataclasses import dataclass


@dataclass
class ExecutionRecord:
    """One executed step."""

    step_name: str
    status: str
    duration: float
    message: str = ""