"""
PDF Reader Utility.

Extracts plain text from PDF documents.

Contains only PDF reading logic and is independent of
embeddings, vector databases and business workflows.
"""

from pypdf import PdfReader
from backend.ingestion.Page import Page

def read_pdf(pdf_path)-> list[Page]:
    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        extracted_text = page.extract_text()
        if extracted_text:
            pages.append(
                Page(
                    page_number=page_number,
                    text=extracted_text
                )
            )

    return pages