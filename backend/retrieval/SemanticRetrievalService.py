"""
Semantic Retrieval Service.

Purpose:
    Retrieves relevant knowledge using vector similarity search.

Responsibilities:
    - Generate query embeddings
    - Perform vector search
    - Return the most relevant Knowledge Nodes

Does NOT:
    - Perform keyword search
    - Build prompts
    - Call the LLM
    - Merge retrieval results
"""


class SemanticRetrievalService:

    def __init__(
        self,
        embedding_service,
        vector_repository
    ):

        self.embedding_service = embedding_service
        self.vector_repository = vector_repository

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        where: dict | None = None
    ):
        """Retrieve relevant knowledge using semantic search."""

        query_embedding = self.embedding_service.get_embedding(question)

        return self.vector_repository.search(
            query_embedding=query_embedding,
            top_k=top_k,
            where=where
        )