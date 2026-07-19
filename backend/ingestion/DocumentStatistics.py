"""
Document Statistics.

Purpose:
    Represents summary information about the indexed knowledge base.

Responsibilities:
    - Store document statistics
    - Provide a simple data model for presentation

Does NOT:
    - Query repositories
    - Calculate statistics
    - Modify documents
"""


from dataclasses import dataclass


@dataclass
class DocumentStatistics:
    total_documents: int
    total_chunks: int