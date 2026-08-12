"""
Source Quote Validation Tests.

Purpose:
    Protect Project Niyam against unsupported or paraphrased
    extracted facts being accepted as source-grounded knowledge.

Responsibilities:
    - Verify exact source quotes are accepted.
    - Verify formatting-only differences are accepted.
    - Verify paraphrases are rejected.
    - Verify invented continuations are rejected.
    - Verify unrelated statements are rejected.

Does NOT:
    - Test LLM behaviour.
    - Test retrieval.
    - Test knowledge extraction.
    - Depend on Ollama.
"""


from backend.extraction.SourceQuoteValidator import (
    SourceQuoteValidator,
)


def _create_validator() -> SourceQuoteValidator:
    """Create the source quote validator under test."""

    return SourceQuoteValidator()


def test_exact_quote_is_accepted() -> None:
    """Accept a quote that exists exactly in the source."""

    validator = _create_validator()

    source = (
        "Company A\n"
        "Built a billing platform."
    )

    quote = "Built a billing platform."

    assert validator.is_supported(
        source_quote=quote,
        source_text=source,
    )


def test_whitespace_difference_is_accepted() -> None:
    """Accept formatting-only whitespace differences."""

    validator = _create_validator()

    source = (
        "Company A\n"
        "Built a billing platform."
    )

    quote = "Built    a billing platform."

    assert validator.is_supported(
        source_quote=quote,
        source_text=source,
    )


def test_paraphrase_is_rejected() -> None:
    """Reject a quote that changes the source wording."""

    validator = _create_validator()

    source = (
        "Company A\n"
        "Built a billing platform."
    )

    quote = "Developed a billing system."

    assert not validator.is_supported(
        source_quote=quote,
        source_text=source,
    )


def test_invented_continuation_is_rejected() -> None:
    """Reject a quote containing unsupported additional information."""

    validator = _create_validator()

    source = (
        "Company A\n"
        "Built a billing platform."
    )

    quote = (
        "Built a billing platform "
        "and reduced processing time by 40%."
    )

    assert not validator.is_supported(
        source_quote=quote,
        source_text=source,
    )


def test_unrelated_source_is_rejected() -> None:
    """Reject a quote that does not exist in the source."""

    validator = _create_validator()

    source = (
        "Company A\n"
        "Built a billing platform."
    )

    quote = "Opened a new international office."

    assert not validator.is_supported(
        source_quote=quote,
        source_text=source,
    )