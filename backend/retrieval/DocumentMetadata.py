from dataclasses import dataclass


@dataclass
class DocumentMetadata:
    document_id: str
    source: str
    page_number: int
    chunk_number: int