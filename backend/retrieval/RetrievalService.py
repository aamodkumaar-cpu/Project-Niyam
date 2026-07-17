"""
Retrieval Service.

Purpose:
    Coordinates multiple retrieval strategies.

Responsibilities:
    - Execute semantic retrieval
    - Execute keyword retrieval
    - Merge retrieval results
    - Return relevant knowledge nodes

Does NOT:
    - Build prompts
    - Call the LLM
"""


from backend.retrieval.KnowledgeNode import KnowledgeNode


class RetrievalService:

    def __init__(
        self,
        semantic_retrieval_service,
        keyword_retrieval_service,
        result_merger
    ):

        self.semantic_retrieval_service = semantic_retrieval_service
        self.keyword_retrieval_service = keyword_retrieval_service
        self.result_merger = result_merger

    
    
    def retrieve(
        self,
        question: str,
        where: dict | None = None
    )-> list[KnowledgeNode] : 
        """Retrieve knowledge using all configured retrieval strategies."""

        semantic_nodes = self.semantic_retrieval_service.retrieve(
            question=question,
            where=where
        )

        keyword_nodes = self.keyword_retrieval_service.retrieve(
            question
        )

        return self.result_merger.merge(
            semantic_nodes=semantic_nodes,
            keyword_nodes=keyword_nodes
        )