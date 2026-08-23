"""
Vector Repository.

Type:
    Repository

Purpose:
    Provides all persistence operations for the vector database.

Responsibilities:
    - Store document embeddings.
    - Perform semantic similarity search.
    - Perform keyword search.
    - Retrieve indexed chunks.
    - Map Chroma records into domain objects.

Does NOT:
    - Generate embeddings.
    - Read PDF files.
    - Build prompts.
    - Perform ranking.
"""


import re

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.types import Metadata
from chromadb.types import Where

from backend.config.settings import (
    CHROMA_DB_PATH,
    VECTOR_COLLECTION,
)
from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.retrieval.DocumentMetadata import DocumentMetadata
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
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

    _KEYWORD_STOP_WORDS: frozenset[str] = frozenset({
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "this",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
        "each",
        "other",
        "associated",
    })

    client: ClientAPI
    collection: Collection
    keyword_tokenizer: KeywordTokenizer
    keyword_scorer: KeywordScorer

    def __init__(
        self,
        keyword_tokenizer: KeywordTokenizer,
        keyword_scorer: KeywordScorer,
    ) -> None:
        """Initialize the Chroma collection."""

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=VECTOR_COLLECTION
        )

        self.keyword_tokenizer = keyword_tokenizer
        self.keyword_scorer = keyword_scorer

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

        return [
            KnowledgeNode(
                content=document,
                score=distance,
                semantic_distance=distance,
                metadata=self._to_document_metadata(metadata)
            )
            for document, metadata, distance in zip(
                documents[0],
                metadatas[0],
                distances[0],
                strict=False
            )
        ]

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

        return [
            KnowledgeNode(
                content=document,
                score=0.0,
                metadata=self._to_document_metadata(metadata)
            )
            for document, metadata in zip(
                documents,
                metadatas,
                strict=False
            )
        ]

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

        return [
            KnowledgeNode(
                content=document,
                score=0.0,
                metadata=self._to_document_metadata(metadata)
            )
            for document, metadata in zip(
                documents,
                metadatas,
                strict=False
            )
        ]

    def keyword_search(
        self,
        question: str,
        top_k: int = 5,
        where: Where | None = None
    ) -> list[KnowledgeNode]:
        """Retrieve knowledge using weighted keyword matching."""

        candidates = self.get_chunks(
            where=where
        )

        if not candidates:
            return []

        question_tokens = self._get_question_tokens(
            question
        )

        if not question_tokens:
            return []

        scored_nodes: list[tuple[float, KnowledgeNode]] = []

        for node in candidates:

            if self._is_question_or_activity_chunk(
                node.content
            ):
                continue

            content_tokens = self.keyword_tokenizer.tokenize(
                node.content
            )

            keyword_score = self.keyword_scorer.score(
                query_tokens=question_tokens,
                content_tokens=content_tokens,
            )

            if keyword_score <= 0.0:
                continue

            node.keyword_score = keyword_score
            node.score = keyword_score

            scored_nodes.append(
                (
                    keyword_score,
                    node,
                )
            )

        scored_nodes.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            node
            for _, node in scored_nodes[:top_k]
        ]

    def document_exists(
        self,
        document_id: str
    ) -> bool:
        """Return True if the document has already been indexed."""

        results = self.collection.get(
            where={
                "document_id": document_id
            },
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

    def _get_question_tokens(
        self,
        question: str,
    ) -> list[str]:
        """Return meaningful normalized question tokens."""

        tokens = self.keyword_tokenizer.tokenize(
            question
        )

        return [
            token
            for token in tokens
            if len(token) >= 3
            and token not in self._KEYWORD_STOP_WORDS
        ]

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

    def _is_question_chunk(
        self,
        content: str,
    ) -> bool:
        """Return whether the chunk is structurally a question."""

        stripped = content.strip()

        if "?" in stripped:
            return True

        question_starters = (
            "who ",
            "what ",
            "when ",
            "where ",
            "why ",
            "how ",
            "which ",
            "whom ",
            "whose ",
            "can ",
            "could ",
            "would ",
            "should ",
            "is ",
            "are ",
            "was ",
            "were ",
            "do ",
            "does ",
            "did ",
        )

        return stripped.lower().startswith(question_starters)

    def _is_question_or_activity_chunk(
        self,
        content: str,
    ) -> bool:
        """Return whether source content is primarily a question or activity."""

        normalized = " ".join(
            content.split()
        ).strip()

        if not normalized:
            return True

        question_count = normalized.count("?")

        numbered_question_count = len(
            re.findall(
                r"\b\d+\.\s+.*?\?",
                normalized,
            )
        )

        instruction_count = len(
            re.findall(
                r"\b(?:explain|discuss|develop|prepare|create|"
                r"document|translate|divide|identify|describe|"
                r"compare|write|list|state|observe)\b",
                normalized,
                flags=re.IGNORECASE,
            )
        )

        if numbered_question_count >= 2:
            return True

        if question_count >= 2:
            return True

        if instruction_count >= 2 and question_count >= 1:
            return True

        if question_count == 1:
            return True

        return False