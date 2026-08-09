"""
Console Logger.

Type:
    Diagnostic Service

Purpose:
    Writes log messages to the console.

Responsibilities:
    - Print log messages
    - Filter messages based on log level
    - Allow runtime log level changes

Does NOT:
    - Persist logs
    - Execute workflows
"""

from backend.diagnostic.LogLevel import LogLevel
from backend.diagnostic.Logger import Logger


class ConsoleLogger(Logger):
    """Console logger."""

    level: LogLevel

    def __init__(
        self,
        level: LogLevel = LogLevel.INFO
    ) -> None:
        """Initialize the logger."""

        self.level = level

    def set_level(
        self,
        level: LogLevel
    ) -> None:
        """Change the log level."""

        self.level = level

    def debug(
        self,
        message: str
    ) -> None:

        if self.level <= LogLevel.DEBUG:
            print(message)

    def info(
        self,
        message: str
    ) -> None:

        if self.level <= LogLevel.INFO:
            print(message)

    def warning(
        self,
        message: str
    ) -> None:

        if self.level <= LogLevel.WARNING:
            print(message)

    def error(
        self,
        message: str
    ) -> None:

        if self.level <= LogLevel.ERROR:
            print(message)