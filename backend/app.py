from backend.application import Application
from pathlib import Path
from backend.ingestion.IngestionService import IngestionService
from backend.config.settings import DOCUMENTS_DIR


if __name__ == "__main__":
    print("\nProject-Niyam is running...\n")

    ingestion_service = IngestionService()

    ingestion_service.ingest_document(
        document_id="resume",
        pdf_path=Path(DOCUMENTS_DIR / "Amod Kumar-Senior Engineering Leader.pdf")
    )
    app = Application()
   
    while True:
        query = input("Ask question: ")
        if query.lower() in ["exit", "quit"]:
            break

        result = app.search(query)

        print("\nAnswer")
        print("------")
        print(result.answer)