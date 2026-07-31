"""
Prompt Builder.

Purpose:
    Constructs prompts for the Language Model.

Responsibilities:
    - Format retrieved knowledge
    - Combine question and context
    - Produce the final prompt

Does NOT:
    - Retrieve documents
    - Call the LLM
    - Modify retrieved knowledge
"""


class PromptBuilder:

    def build(
        self,
        question: str,
        knowledge_nodes
    ) -> list[dict]:

        context = ""

        for node in knowledge_nodes:

            context += (
                f"Source : {node.metadata.source}\n"
                f"Page   : {node.metadata.page_number}\n"
                f"\n"
                f"{node.content}\n"
                "----------------------------------------\n"
            )

        messages = [

            {
                "role": "system",
                "content": """
                    You are Project Niyam.

                    Use ONLY the supplied context.
                    Do not use external knowledge.
                    If the answer exists in the context, answer it.
                    If the context contains only a partial mention, state exactly what is mentioned.
                    If the topic is completely absent, reply:

                    "I could not find the answer in the available documents."
                    """
            },

            {
                "role": "user",
                "content": f"""
                    Context
                    =======

                    {context}

Question
=======
{question}
                    """
            }

        ]

        return messages