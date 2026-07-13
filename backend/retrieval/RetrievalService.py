class RetrievalService:

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
        top_k: int = 5
    ):
        query_embedding = self.embedding_service.get_embedding(question)

        return self.vector_repository.search(
            query_embedding=query_embedding,
            top_k=top_k
        )