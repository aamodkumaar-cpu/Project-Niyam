"""
Chunk Inspector.

Purpose:
    Provides visibility into the chunking stage.

Responsibilities:
    - Display generated chunks
    - Display page number
    - Display chunk number
    - Display chunk length
    - Display a preview of each chunk

Does NOT:
    - Modify chunks
    - Perform chunking
    - Store chunks
"""


class ChunkInspector:

    @staticmethod
    def inspect(chunks):

        print()
        print("=" * 80)
        print("CHUNK INSPECTOR")
        print("=" * 80)

        print(f"\nTotal Chunks : {len(chunks)}\n")

        for chunk in chunks:

            print("-" * 80)

            print(f"Chunk  : {chunk.chunk_number}")
            print(f"Page   : {chunk.page_number}")
            print(f"Length : {len(chunk.text)}")

            preview = chunk.text[:250].replace("\n", " ")

            print("\nPreview:")
            print(preview)

        print("-" * 80)
        print()