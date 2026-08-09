"""
Vector Repository.

Type:
    Repository

Purpose:
    Provides all persistence operations for the vector database.

Responsibilities:
    - Store document embeddings.
    - Perform semantic similarity search.
    - Retrieve indexed chunks.
    - Map Chroma records into domain objects.

Does NOT:
    - Generate embeddings.
    - Read PDF files.
    - Build prompts.
    - Perform ranking.
"""


import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.types import Where
from chromadb.types import Metadata

from backend.config.settings import (
    CHROMA_DB_PATH,
    VECTOR_COLLECTION,
)
from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KnowledgeNode import KnowledgeNode


# ---------------------------------------------------------------------
# Metadata Conversion Helpers
# ---------------------------------------------------------------------

def _coerce_str(
    value: object,
    default: str = ""
) -> str:
    """Safely convert an arbitrary object into a string."""

    if isinstance(value, str):
        return value

    if value is None:
        return default

    return str(value)


def _coerce_int(
    value: object,
    default: int = 0
) -> int:
    """Safely convert an arbitrary object into an integer."""

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default

    return default


# ---------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------


class VectorRepository:
    """Provides persistence operations for the vector database."""

    client: ClientAPI
    collection: Collection

    def __init__(self) -> None:
        """Initialize the Chroma collection."""

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=VECTOR_COLLECTION
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def store_document(
        self,
        document_id: str,
        document: str,
        embedding: list[float],
        metadata: Metadata
    ) -> None:
        """Store one document chunk."""

        self.collection.add(
            ids=[document_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """Perform semantic similarity search."""

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )

        documents = results.get("documents")
        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if not documents or not metadatas or not distances:
            return []

        return self._build_knowledge_nodes(
            documents=documents[0],
            metadatas=metadatas[0],
            scores=distances[0]
        )

    def get_all_chunks(self) -> list[KnowledgeNode]:
        """Return every indexed chunk."""

        results = self.collection.get(
            include=[
                "documents",
                "metadatas"
            ]
        )

        documents = results.get("documents")
        metadatas = results.get("metadatas")

        if not documents or not metadatas:
            return []

        return self._build_knowledge_nodes(
            documents=documents,
            metadatas=metadatas,
            scores=[0.0] * len(documents)
        )

    def get_chunks(
        self,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """Return all chunks matching the supplied metadata filter."""

        results = self.collection.get(
            where=where,
            include=[
                "documents",
                "metadatas"
            ]
        )

        documents = results.get("documents")
        metadatas = results.get("metadatas")

        if not documents or not metadatas:
            return []

        return self._build_knowledge_nodes(
            documents=documents,
            metadatas=metadatas,
            scores=[0.0] * len(documents)
        )

    def document_exists(
        self,
        document_id: str
    ) -> bool:
        """Return True if the document has already been indexed."""

        results = self.collection.get(
            where={"document_id": document_id},
            limit=1
        )

        return len(results["ids"]) > 0

    def delete_document(
        self,
        document_id: str
    ) -> None:
        """Delete every chunk belonging to the supplied document."""

        _ = self.collection.delete(
            where={
                "document_id": document_id
            }
        )

    def count_chunks(self) -> int:
        """Return the total number of indexed chunks."""

        return self.collection.count()

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    def _build_knowledge_nodes(
        self,
        documents: list[str],
        metadatas: list[Metadata],
        scores: list[float]
    ) -> list[KnowledgeNode]:
        """Convert Chroma results into KnowledgeNode objects."""

        return [
            self._to_knowledge_node(
                document=document,
                metadata=metadata,
                score=score
            )
            for document, metadata, score in zip(
                documents,
                metadatas,
                scores
            )
        ]

    def _to_knowledge_node(
        self,
        document: str,
        metadata: Metadata,
        score: float
    ) -> KnowledgeNode:
        """Create a KnowledgeNode."""

        return KnowledgeNode(
            content=document,
            score=score,
            metadata=self._to_document_metadata(
                metadata
            )
        )

    def _to_document_metadata(
        self,
        metadata: Metadata
    ) -> DocumentMetadata:
        """Convert Chroma metadata into DocumentMetadata."""

        domain_value = metadata.get(
            "domain",
            KnowledgeDomain.GENERAL.value
        )

        return DocumentMetadata(
            document_id=_coerce_str(
                metadata.get("document_id")
            ),
            source=_coerce_str(
                metadata.get("source")
            ),
            page_number=_coerce_int(
                metadata.get("page_number")
            ),
            chunk_number=_coerce_int(
                metadata.get("chunk_number")
            ),
            domain=KnowledgeDomain(
                _coerce_str(domain_value)
            ),
            compliance_pack=_coerce_str(
                metadata.get("compliance_pack")
            )
        )



    def keyword_search(
        self,
        question: str,
        top_k: int = 5,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """
        Retrieve knowledge using keyword matching.
        """

        candidates = self.get_chunks(
            where=where
        )

        if not candidates:
            return []

        question_words = {
            word.strip(".,:;!?()[]{}\"'").lower()
            for word in question.split()
            if len(word) >= 3
        }

        scored_nodes: list[tuple[int, KnowledgeNode]] = []

        for node in candidates:

            content_words = {
                word.strip(".,:;!?()[]{}\"'").lower()
                for word in node.content.split()
            }

            score = len(
                question_words.intersection(
                    content_words
                )
            )

            if score > 0:
                scored_nodes.append(
                    (score, node)
                )

        scored_nodes.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            node
            for _, node in scored_nodes[:top_k]
        ]