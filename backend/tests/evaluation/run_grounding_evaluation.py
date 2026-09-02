"""
Project Niyam Grounding Evaluation Runner.

Purpose:

    Run a fixed set of representative knowledge questions through the
    production application wiring and capture the complete execution log.

Responsibilities:

    - Create the production ServiceRegistry.
    - Run representative grounding questions.
    - Use the same request-routing path as the CLI application.
    - Use the same console renderers as the CLI application.
    - Persist the complete evaluation run to a timestamped log file.

Does NOT:

    - Modify production services.
    - Modify retrieval or extraction behavior.
    - Assert expected answers.
    - Replace the application's normal execution path.
"""

from __future__ import annotations

import contextlib
import io
from datetime import datetime
from pathlib import Path

from backend.bootstrap.ServiceRegistry import ServiceRegistry
from backend.presentation.ConsoleRenderer import ConsoleRenderer
from backend.compliance.BusinessProfile import BusinessProfile


QUESTIONS: tuple[str, ...] = (
    "What was Amod's role at Cloudera?",
    "What did Amod do at Cloudera?",
    "What did Amod accomplish at Cloudera?",
    "What was Amod's role at Oracle?",
    "What did Amod do at Oracle?",
    "What did Amod accomplish at Oracle?",
    "What was Amod's role at 24[7].ai?",
    "What did Amod do at 24[7].ai?",
    "What did Amod accomplish at 24[7].ai?",
    "How did Amod improve developer productivity at Cloudera?",
    "What did Amod do to improve platform availability at Cloudera?",
    "What companies did Amod work for?",
    "What is GST registration?",
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

LOG_DIRECTORY = (
    PROJECT_ROOT
    / "backend"
    / "tests"
    / "evaluation"
    / "evaluation_logs"
)


def _create_log_path() -> Path:
    """Create a timestamped evaluation log path."""

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return (
        LOG_DIRECTORY
        / f"grounding_evaluation_{timestamp}.log"
    )


def _run_question(
    registry: ServiceRegistry,
    question_number: int,
    question: str,
) -> None:
    """Run one question through the production request path."""

    print()
    print("=" * 80)
    print(
        f"QUESTION {question_number}/{len(QUESTIONS)}"
    )
    print("=" * 80)
    print()
    print(
        f"Question : {question}"
    )
    print()

    execution = registry.request_router.route(
        question=question,
        where=None,
    )

    if execution.answer is not None:
        ConsoleRenderer.render_answer(
            execution.answer
        )

    ConsoleRenderer.render_execution_trace(
        execution.trace
    )


def main() -> None:
    """Run the complete grounding evaluation."""

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_path = _create_log_path()

    captured_output = io.StringIO()

    print("=" * 80)
    print("PROJECT NIYAM - GROUNDING EVALUATION")
    print("=" * 80)
    print()
    print(
        f"Questions : {len(QUESTIONS)}"
    )
    print()
    print(
        "Running production application wiring..."
    )
    print()

    with contextlib.redirect_stdout(
        captured_output
    ):
        print("=" * 80)
        print("PROJECT NIYAM - GROUNDING EVALUATION")
        print("=" * 80)
        print()
        print(
            f"Started : "
            f"{datetime.now().isoformat(timespec='seconds')}"
        )
        print(
            f"Questions : {len(QUESTIONS)}"
        )
        print()

        registry = ServiceRegistry()

        registry.business_profile_session.set_business_profile(
            BusinessProfile(
                business_name="Evaluation Business",
                industry="Manufacturing",
                company_size=5,
                state="Delhi",
            )
        )

        for index, question in enumerate(
            QUESTIONS,
            start=1,
        ):
            print(
                f"\n>>> Running question "
                f"{index}/{len(QUESTIONS)}: "
                f"{question}"
            )

            try:
                _run_question(
                    registry=registry,
                    question_number=index,
                    question=question,
                )

            except Exception as exc:
                print()
                print("=" * 80)
                print(
                    f"QUESTION {index} FAILED"
                )
                print("=" * 80)
                print()
                print(
                    f"Question : {question}"
                )
                print(
                    f"Exception : "
                    f"{type(exc).__name__}: {exc}"
                )
                print()

        print()
        print("=" * 80)
        print("EVALUATION COMPLETE")
        print("=" * 80)
        print()
        print(
            f"Completed : {len(QUESTIONS)}"
        )

    log_path.write_text(
        captured_output.getvalue(),
        encoding="utf-8",
    )

    print("=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    print()
    print(
        f"Questions : {len(QUESTIONS)}"
    )
    print(
        f"Log file  : {log_path}"
    )
    print()


if __name__ == "__main__":
    main()
