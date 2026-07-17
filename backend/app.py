"""
Project Niyam Entry Point.

Starts the application, ingests all available documents,
and launches the interactive question-answering console.
"""


from backend.application import Application
from backend.ingestion.DocumentCatalogRepository import DocumentCatalogRepository
from backend.ingestion.DocumentService import DocumentService
from backend.ingestion.IngestionService import IngestionService
from backend.config.settings import DOCUMENTS_DIR
from backend.presentation.ConsoleRenderer import ConsoleRenderer


if __name__ == "__main__":

    print("\nProject Niyam is running...\n")

    ingestion_service = IngestionService()

    document_repository = DocumentCatalogRepository(
        DOCUMENTS_DIR
    )
    document_service = DocumentService(
        document_repository
    )       
    for document in document_service.list_documents():

        print(f"Ingesting: {document.name}")

        ingestion_service.ingest_document(
            document
        )

    documents = document_service.list_documents()
    print("\nIndexed Documents")
    print("-----------------")

    print("\nSearch Scope")
    print("------------")
    print("0. All Documents")
    for index, document in enumerate(documents, start=1):
        print(f"{index}. {document.name}")

    selection = int(input("\nChoose: "))
    print("selection:: ", selection)
    
    app = Application()
    while True:

        query = input("Ask question: ")

        if query.lower() in ["exit", "quit"]:
            break

        result = app.search(query)

        ConsoleRenderer.render(result)