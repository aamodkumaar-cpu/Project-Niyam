"""
Answer Result.

Purpose:
    Represents the final response produced by Project Niyam.

Responsibilities:
    - Hold the generated answer
    - Hold source metadata
    - Provide a single response object to callers

Does NOT:
    - Generate answers
    - Retrieve documents
    - Call the LLM
"""

from dataclasses import dataclass

from backend.retrieval.DocumentMetadata import DocumentMetadata


@dataclass
class AnswerResult:

    answer: str

    sources: list[DocumentMetadata]