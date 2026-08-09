"""
Log Level.

Type:
    Runtime Model

Purpose:
    Represents the current logging verbosity.

Responsibilities:
    - Define supported logging levels

Does NOT:
    - Perform logging
    - Store log messages
"""

from enum import IntEnum


class LogLevel(IntEnum):
    """Supported logging levels."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    OFF = 100