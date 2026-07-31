"""
Project Niyam Entry Point.

Starts the application, ingests all available documents,
and launches the interactive question-answering console.
"""


from backend.application import Application
from backend.compliance.BusinessProfile import BusinessProfile
from backend.compliance.BusinessProfileCollector import BusinessProfileCollector
from backend.ingestion.Document import Document
from backend.ingestion.DocumentCatalogRepository import DocumentCatalogRepository
from backend.ingestion.DocumentService import DocumentService
from backend.ingestion.DocumentStatistics import DocumentStatistics
from backend.ingestion.IngestionService import IngestionService
from backend.config.settings import DOCUMENTS_DIR
from backend.presentation.ConsoleRenderer import ConsoleRenderer
from backend.retrieval.VectorRepository import VectorRepository
from backend.orchestration.RequestRouter import RequestRouter



def show_startup_banner(
        statistics: DocumentStatistics
    ) -> None:
        """Display knowledge base information."""

        print("=" * 60)
        print("Project Niyam")
        print("AI Compliance Officer for Indian SMBs")
        print("=" * 60)

        print("\nKnowledge Base")
        print("--------------")
        print(f"Documents : {statistics.total_documents}")
        print(f"Chunks    : {statistics.total_chunks}")



def choose_search_scope(
        documents: list[Document]
    ) -> dict | None:
        """Return the selected document filter."""

        print("\nSearch Scope")
        print("------------")

        print("0. All Documents")

        for index, document in enumerate(documents, start=1):
            print(f"{index}. {document.name}")

        while True:
            try:
                selection = int( input("\nChoose: ") )

                if 0 <= selection <= len(documents):
                    break
                print("Invalid selection.")
            except ValueError:
                print("Please enter a number.")

        if selection == 0:
            return None

        selected_document = documents[selection - 1]

        return {
            "document_id": selected_document.id
        }


if __name__ == "__main__":

    ingestion_service = IngestionService()
    vector_repository = VectorRepository()

    document_repository = DocumentCatalogRepository(
        DOCUMENTS_DIR
    )
    document_service = DocumentService(
        document_repository=document_repository,
        vector_repository=vector_repository
    )   


    documents = document_service.list_documents()
    for document in documents:
        print(f"Ingesting: {document.name}")
        ingestion_service.ingest_document(document)

    statistics = document_service.get_statistics()
    show_startup_banner( statistics )
    where = choose_search_scope( documents )
   
    app=Application()
    router = RequestRouter(app)

    collector = BusinessProfileCollector()
    business_profile = collector.collect()
    app.set_business_profile(business_profile)
    checklist = app.generate_compliance_checklist(app.get_business_profile())
    

    ConsoleRenderer.render_compliance_checklist( checklist )

    while True:
        query = input("Ask question: ")
        if query.lower() in ["exit", "quit"]:
            break


        result = router.route(
            question=query,
            where=where
        )

        ConsoleRenderer.render(result)


    