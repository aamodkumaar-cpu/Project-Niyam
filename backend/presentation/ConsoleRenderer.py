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

from backend.orchestration.ExecutionTrace import ExecutionTrace
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
    def render_answer(
        result: AnswerResult
    ):
        """Render an answer."""

        print("\nAnswer")
        print("-" * 80)

        print(result.answer)

        print("\nSources")
        print("-" * 80)

        if not result.sources:
            print("No sources identified.")

        else:

            unique_sources = sorted(
                {
                    (
                        source.source,
                        source.page_number
                    )
                    for source in result.sources
                }
            )

            for index, (document, page) in enumerate(
                unique_sources,
                start=1
            ):
                print(
                    f"{index}. {document} (Page {page})"
                )

        print("-" * 80)
        print()


    @staticmethod
    def render_execution_trace(
        trace: ExecutionTrace
    ):
        """Render workflow execution."""

        print("\nExecution Summary")
        print("-" * 80)

        for record in trace.records:

            icon = {
                "SUCCESS": "✔",
                "FAILED": "✖",
                "SKIPPED": "⏭"
            }.get(
                record.status,
                "•"
            )

            print(
                f"{icon} {record.step_name:<35}"
                f" ({record.duration:.2f}s)"
            )

            if record.message:
                print(
                    f"    {record.message}"
                )

        print("-" * 80)
        print()