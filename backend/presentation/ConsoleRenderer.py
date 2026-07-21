"""
Console Renderer.

Purpose:
    Displays application results on the console.

Responsibilities:
    - Render answers
    - Render sources
    - Format console output

Does NOT:
    - Generate answers
    - Retrieve documents
    - Call the LLM
"""

from backend.results.AnswerResult import AnswerResult


class ConsoleRenderer:

    @staticmethod
    def render_compliance_checklist(
        checklist
        ):

        """Render a compliance checklist."""

        print("\nCompliance Checklist")
        print("-" * 80)

        for item in checklist.items:
            status = "✓" if item.mandatory else "-"
            print(f"{status} {item.title}")
            print(f"  {item.description}")
            print()




    @staticmethod
    def render(
        result: AnswerResult
    ):

        print("\n")
        print("=" * 80)

        print("\nAnswer")
        print("-" * 80)

        print(result.answer)

        print("\nSources")
        print("-" * 80)

        for index, source in enumerate(result.sources, start=1):

            print(
                f"{index}. "
                f"{source.source} "
                f"(Page {source.page_number})"
            )

        print("\n" + "=" * 80)

    