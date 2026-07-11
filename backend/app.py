"""
Project Niyam - Application Entry Point.

Starts the application and coordinates user interactions.

This file should remain lightweight and delegate business
logic to the appropriate services.
"""
import os
from backend.ingestion.IngestionService import IngestionService
from backend.config.settings import DOCUMENTS_DIR, UPLOADS_DIR


def main():

    ingestion_service = IngestionService()

    ingestion_service.ingest_document(
        document_id="resume",
        pdf_path=os.path.join(DOCUMENTS_DIR, "Amod Kumar-Senior Engineering Leader.pdf")
    )

    print("\nDocument successfully indexed.\n")



if __name__ == "__main__":
    main()