"""
Logger.

Type:
    Diagnostic Service

Purpose:
    Defines the logging contract.

Responsibilities:
    - Log debug messages
    - Log info messages
    - Log warning messages
    - Log error messages
    - Change logging level at runtime

Does NOT:
    - Store log history
    - Execute workflows
"""

from abc import ABC, abstractmethod

from backend.diagnostic.LogLevel import LogLevel


class Logger(ABC):
    """Logging abstraction."""

    @abstractmethod
    def set_level(
        self,
        level: LogLevel
    ) -> None:
        """Update the current log level."""

    @abstractmethod
    def debug(
        self,
        message: str
    ) -> None:
        """Log a debug message."""

    @abstractmethod
    def info(
        self,
        message: str
    ) -> None:
        """Log an info message."""

    @abstractmethod
    def warning(
        self,
        message: str
    ) -> None:
        """Log a warning message."""

    @abstractmethod
    def error(
        self,
        message: str
    ) -> None:
        """Log an error message."""