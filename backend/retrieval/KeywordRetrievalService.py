"""
Keyword Retrieval Service.

Purpose:
    Retrieves relevant knowledge using keyword matching.

Responsibilities:
    - Search chunks using keywords
    - Rank matching chunks
    - Return the best matching Knowledge Nodes

Does NOT:
    - Generate embeddings
    - Perform vector search
    - Build prompts
    - Call the LLM
"""

from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeNode import KnowledgeNode

class KeywordRetrievalService:

    def __init__(
        self,
        vector_repository
    ):

        self.vector_repository = vector_repository
        self.tokenizer = KeywordTokenizer()

    def retrieve(
        self,
        question: str,
        top_k: int = 5
    ):
        keywords = self.tokenizer.tokenize(question)
        knowledge_nodes = self.vector_repository.get_all_chunks()
        scored_nodes = []

        for node in knowledge_nodes:
            score = self._score_chunk(
                keywords=keywords,
                chunk=node
            )

            if score > 0:
                scored_nodes.append(
                    (
                        score,
                        node
                    )
                )
        scored_nodes.sort(
            key=lambda item: item[0],
            reverse=True
        )
        
        return [
            node
            for _, node in scored_nodes[:top_k] #The underscore (_) is the Python convention for "this value exists, but I'm not using it."
        ]


    def _score_chunk(
        self,
        keywords: list[str],
        chunk: KnowledgeNode
    ) -> int:

        content = chunk.content.lower()
        score = 0
        for keyword in keywords:
            score += content.count(keyword)

        return score