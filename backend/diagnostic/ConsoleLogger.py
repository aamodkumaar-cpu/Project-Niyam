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

from typing import override

from backend.diagnostic.LogLevel import LogLevel
from backend.diagnostic.Logger import Logger


class ConsoleLogger(Logger):
    """Console logger."""

    level: LogLevel

    def __init__(
        self,
        level: LogLevel = LogLevel.INFO,
    ) -> None:
        """Initialize the logger."""

        self.level = level

    def set_level(
        self,
        level: LogLevel,
    ) -> None:
        """Change the log level."""

        self.level = level

    @override
    def debug(
        self,
        message: str,
    ) -> None:
        """Write a debug message when debug logging is enabled."""

        if self.level <= LogLevel.DEBUG:
            print(message)

    @override
    def info(
        self,
        message: str,
    ) -> None:
        """Write an info message when info logging is enabled."""

        if self.level <= LogLevel.INFO:
            print(message)

    @override
    def warning(
        self,
        message: str,
    ) -> None:
        """Write a warning message when warning logging is enabled."""

        if self.level <= LogLevel.WARNING:
            print(message)

    @override
    def error(
        self,
        message: str,
    ) -> None:
        """Write an error message when error logging is enabled."""

        if self.level <= LogLevel.ERROR:
            print(message)