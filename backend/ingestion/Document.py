"""
Document domain model.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    id: str
    name: str
    path: str