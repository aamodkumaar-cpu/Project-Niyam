from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    page_number: int