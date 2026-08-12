"""
Extraction Response Parser Tests.

Purpose:
    Protect the boundary between raw LLM output and deterministic source
    candidate selection.
"""

from backend.extraction.ExtractionResponseParser import ExtractionResponseParser


def test_valid_candidate_selection_is_parsed() -> None:
    """Accept a valid candidate selection response."""

    result = ExtractionResponseParser().parse(
        '[{"candidate_id":"C1_2","confidence":1.0}]'
    )

    assert result == [
        {
            "candidate_id": "C1_2",
            "confidence": 1.0,
        }
    ]


def test_markdown_wrapped_json_is_parsed() -> None:
    """Accept JSON wrapped in a Markdown code fence."""

    result = ExtractionResponseParser().parse(
        "```json\n"
        "[{\"candidate_id\":\"C1_2\",\"confidence\":1.0}]\n"
        "```"
    )

    assert result == [
        {
            "candidate_id": "C1_2",
            "confidence": 1.0,
        }
    ]


def test_malformed_json_is_rejected() -> None:
    """Reject malformed JSON."""

    assert ExtractionResponseParser().parse(
        '[{"candidate_id":"C1_2"'
    ) == []


def test_non_array_response_is_rejected() -> None:
    """Reject a response that is not an array."""

    assert ExtractionResponseParser().parse(
        '{"candidate_id":"C1_2","confidence":1.0}'
    ) == []


def test_missing_candidate_id_is_rejected() -> None:
    """Reject a record without a candidate identifier."""

    assert ExtractionResponseParser().parse(
        '[{"confidence":1.0}]'
    ) == []


def test_missing_confidence_is_rejected() -> None:
    """Reject a record without confidence."""

    assert ExtractionResponseParser().parse(
        '[{"candidate_id":"C1_2"}]'
    ) == []


def test_invalid_confidence_is_rejected() -> None:
    """Reject non-numeric confidence."""

    assert ExtractionResponseParser().parse(
        '[{"candidate_id":"C1_2","confidence":"high"}]'
    ) == []


def test_invalid_record_type_is_rejected() -> None:
    """Reject an array containing a non-object item."""

    assert ExtractionResponseParser().parse(
        '["C1_2"]'
    ) == []


def test_generated_source_quote_is_not_part_of_the_contract() -> None:
    """Reject the old quote-authoring contract."""

    assert ExtractionResponseParser().parse(
        '[{"name":"Company A",'
       + '"source_quote":"Invented fact",'
       + '"confidence":1.0}]'
    ) == []