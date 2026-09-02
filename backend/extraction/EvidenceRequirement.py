"""
Evidence Requirement.

Type:

    Domain Model

Purpose:

    Represents the evidence characteristics required to answer
    an extraction question.

Responsibilities:

    - Record whether direct answer evidence is required.
    - Record whether a quantity is required.
    - Record whether temporal evidence is required.
    - Record whether relationship evidence is required.

Does NOT:

    - Interpret source content.
    - Rank candidates.
    - Retrieve knowledge.
    - Call the LLM.
    - Generate answers.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvidenceRequirement:
    """Defines the evidence characteristics required by a question."""

    direct_answer_required: bool = True
    quantity_required: bool = False
    temporal_value_required: bool = False
    relationship_required: bool = False