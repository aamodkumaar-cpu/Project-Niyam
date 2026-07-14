"""
Prompt Inspector.

Purpose:
    Provides visibility into the prompt that is sent to the LLM.

Responsibilities:
    - Display the final prompt
    - Help diagnose prompt engineering issues
    - Verify retrieved knowledge is included

Does NOT:
    - Modify the prompt
    - Call the LLM
    - Change application behavior
"""

from backend.config.settings import DEBUG


class PromptInspector:

    @staticmethod
    def inspect(messages: list[dict]) -> None:

        if not DEBUG:
            return

        print()
        print("=" * 80)
        print("PROMPT INSPECTOR")
        print("=" * 80)

        for message in messages:

            print()

            print("-" * 80)
            print(f"ROLE : {message['role'].upper()}")
            print("-" * 80)

            print(message["content"])

        print()
        print("=" * 80)