"""
Retrieval Inspector.

Purpose:
    Provides visibility into the retrieval stage.

Responsibilities:
    - Display retrieved chunks
    - Display ranking
    - Display similarity scores

Does NOT:
    - Modify retrieval
    - Change ranking
    - Call the LLM
"""

from backend.config.settings import DEBUG


class RetrievalInspector:

    @staticmethod
    def inspect(
        question: str,
        knowledge_nodes
    ) -> None:

        if not DEBUG:
            return

        print()
        print("=" * 80)
        print("RETRIEVAL INSPECTOR")
        print("=" * 80)

        print(f"\nQuestion:\n{question}")

        print("\nRetrieved Knowledge:\n")

        if not knowledge_nodes:
            print("No knowledge nodes retrieved.")
            return

        for rank, node in enumerate(knowledge_nodes, start=1):

            print("-" * 80)
            print(f"Rank       : {rank}")
            print(f"Score      : {node.score:.4f}")
            print(f"Page       : {node.metadata.page_number}")
            print(f"Chunk      : {node.metadata.chunk_number}")

            preview = node.content.replace("\n", " ")

            print(f"\nPreview:\n{preview[:250]}")

        print("-" * 80)