"""
PDF Reader Utility.

Extracts plain text from PDF documents.

Contains only PDF reading logic and is independent of
embeddings, vector databases and business workflows.
"""

from pypdf import PdfReader


def read_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        extracted_text = page.extract_text()

        if extracted_text:
            text += extracted_text

    return text