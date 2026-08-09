"""
Project Niyam Entry Point.

Starts the application, ingests all available documents,
and launches the interactive question-answering console.
"""



from backend.bootstrap.ServiceRegistry import ServiceRegistry
from backend.compliance.BusinessProfileCollector import BusinessProfileCollector
from backend.ingestion.Document import Document
from backend.ingestion.DocumentStatistics import DocumentStatistics
from backend.presentation.ConsoleRenderer import ConsoleRenderer
from chromadb.types import Where


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
    ) -> Where | None:
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

    registry = ServiceRegistry()
    documents = registry.document_service.list_documents()

    for document in documents:
        print(f"Ingesting: {document.name}")
        registry.ingestion_service.ingest_document(
            document
        )

    statistics = registry.document_service.get_statistics()
    show_startup_banner(statistics)
    where = choose_search_scope( documents )
    collector = BusinessProfileCollector()
    business_profile = collector.collect()
    registry.business_profile_session.set_business_profile( business_profile )

    while True:
        question = input("\nAsk Question : ")
        if question.lower() in (
            "exit",
            "quit"
        ):
            break

        execution = registry.request_router.route(
            question=question,
            where=where
        )

        assert execution.answer is not None
        ConsoleRenderer.render_answer( execution.answer  )
        ConsoleRenderer.render_execution_trace( execution.trace )

    