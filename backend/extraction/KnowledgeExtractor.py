"""
KnowledgeExtractor.

Type:
    Domain Service

Purpose:
    Select source-grounded knowledge from deterministic extraction candidates.

Responsibilities:
    - Analyze extraction question constraints.
    - Build deterministic extraction candidates.
    - Rank candidates at fact level.
    - Apply explicit evidence-selection safety constraints.
    - Ask the LLM to select supporting candidates.
    - Validate selected source evidence.
    - Enforce deterministic extraction constraints.
    - Produce structured knowledge.

Does NOT:
    - Retrieve knowledge.
    - Generate final natural-language answers.
    - Invent factual content.
"""

from __future__ import annotations

from backend.diagnostic.ExecutionDebuggerContract import (
    ExecutionDebuggerContract,
)
from backend.extraction.EvidenceRequirement import EvidenceRequirement
from backend.extraction.EvidenceSelectionSafetyGate import (
    EvidenceSelectionSafetyGate,
)
from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.extraction.ExtractionCandidateBuilder import (
    ExtractionCandidateBuilder,
)
from backend.extraction.ExtractionCandidateRanker import (
    ExtractionCandidateRanker,
)
from backend.extraction.ExtractionPromptBuilder import (
    ExtractionPromptBuilder,
)
from backend.extraction.ExtractionQuestionAnalyzer import (
    ExtractionQuestionAnalyzer,
)
from backend.extraction.ExtractionResponseParser import (
    ExtractionResponseParser,
    ExtractionSelection,
)
from backend.extraction.KnowledgeFact import KnowledgeFact
from backend.extraction.KnowledgeSchema import KnowledgeSchema
from backend.extraction.SourceQuoteValidator import (
    SourceQuoteValidator,
)
from backend.extraction.StructuralScopeResolver import (
    StructuralScopeResolver,
)
from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.llm.LLMClient import LLMClient
from backend.llm.Message import Messages
from backend.retrieval.KnowledgeNode import KnowledgeNode


class KnowledgeExtractor:
    """Select structured knowledge from deterministic source candidates."""

    def __init__(
        self,
        prompt_builder: ExtractionPromptBuilder,
        llm_client: LLMClient,
        execution_debugger: ExecutionDebuggerContract,
        knowledge_schema: KnowledgeSchema,
        source_quote_validator: SourceQuoteValidator,
        response_parser: ExtractionResponseParser,
        candidate_builder: ExtractionCandidateBuilder,
        question_analyzer: ExtractionQuestionAnalyzer,
        candidate_ranker: ExtractionCandidateRanker,
        evidence_selection_safety_gate: EvidenceSelectionSafetyGate,
        structural_scope_resolver: StructuralScopeResolver,
    ) -> None:
        """Initialize the knowledge extractor."""

        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.execution_debugger = execution_debugger
        self.knowledge_schema = knowledge_schema
        self.source_quote_validator = source_quote_validator
        self.response_parser = response_parser
        self.candidate_builder = candidate_builder
        self.question_analyzer = question_analyzer
        self.candidate_ranker = candidate_ranker
        self.evidence_selection_safety_gate = (
            evidence_selection_safety_gate
        )
        self.structural_scope_resolver = structural_scope_resolver

    def extract(
        self,
        question: str,
        knowledge_nodes: list[KnowledgeNode],
    ) -> StructuredKnowledge:
        """Select and return only source-grounded knowledge."""

        relationship = (
            self.question_analyzer.is_relationship_question(
                question
            )
        )

        role_question = (
            self.question_analyzer.is_role_question(
                question
            )
        )

        candidates = self.candidate_builder.build(
            knowledge_nodes=knowledge_nodes,
            relationship=relationship,
        )

        if not candidates:
            return StructuredKnowledge()

        evidence_requirement = (
            self.question_analyzer.determine_evidence_requirement(
                question
            )
        )

        ranked_candidates = self.candidate_ranker.rank(
            question=question,
            candidates=candidates,
            evidence_requirement=evidence_requirement,
        )

        safe_candidates = (
            self.evidence_selection_safety_gate.filter(
                question=question,
                candidates=ranked_candidates,
            )
        )

        exhaustive = (
            self.question_analyzer.is_exhaustive_request(
                question
            )
        )

        if exhaustive:
            prompt_candidates = safe_candidates
        else:
            prompt_candidates = (
                self.candidate_ranker.select_for_prompt(
                    question=question,
                    candidates=safe_candidates,
                    evidence_requirement=evidence_requirement,
                )
            )

        if not prompt_candidates:
            return StructuredKnowledge()

        messages: Messages = self.prompt_builder.build(
            question=question,
            candidates=prompt_candidates,
            evidence_requirement=evidence_requirement,
        )

        self.execution_debugger.prompt(messages)

        response = self.llm_client.generate(
            messages=messages,
        )

        self.execution_debugger.raw_llm_response(
            title="Knowledge Selection",
            response=response,
        )

        selections = self.response_parser.parse(response)

        knowledge = self._build_structured_knowledge(
            selections=selections,
            candidates=ranked_candidates,
            allowed_candidates=safe_candidates,
            question=question,
            role_question=role_question,
            exhaustive=exhaustive,
            evidence_requirement=evidence_requirement,
        )

        self.execution_debugger.extraction(knowledge)

        return knowledge

    def _build_structured_knowledge(
        self,
        selections: list[ExtractionSelection],
        candidates: list[ExtractionCandidate],
        allowed_candidates: list[ExtractionCandidate],
        question: str,
        role_question: bool,
        exhaustive: bool,
        evidence_requirement: EvidenceRequirement,
    ) -> StructuredKnowledge:
        """Build structured knowledge from validated extraction selections."""

        allowed_candidate_ids = {
            candidate.candidate_id
            for candidate in allowed_candidates
        }

        knowledge = StructuredKnowledge()

        selected_ids: set[str] = set()
        heading_counts: dict[str, int] = {}

        maximum = (
            self.question_analyzer.extract_max_per_heading(
                question
            )
        )

        self._accept_llm_selections(
            selections=selections,
            candidates=candidates,
            allowed_candidate_ids=allowed_candidate_ids,
            knowledge=knowledge,
            selected_ids=selected_ids,
            heading_counts=heading_counts,
            maximum=maximum,
            role_question=role_question,
            exhaustive=exhaustive,
            evidence_requirement=evidence_requirement,
        )

        if not exhaustive:
            return knowledge

        selected_candidates = [
            candidate
            for candidate in allowed_candidates
            if candidate.candidate_id in selected_ids
        ]

        exhaustive_candidates = (
            self.structural_scope_resolver.resolve(
                selected_candidates=selected_candidates,
                candidates=allowed_candidates,
            )
        )

        self._complete_exhaustive_selection(
            candidates=exhaustive_candidates,
            selections=selections,
            candidate_map={
                candidate.candidate_id: candidate
                for candidate in candidates
            },
            evidence_requirement=evidence_requirement,
            relationship_question=False,
            role_question=role_question,
            max_per_heading=maximum,
            facts=knowledge.facts,
            selected_ids=selected_ids,
            heading_counts=heading_counts,
        )

        return knowledge

    def _accept_llm_selections(
        self,
        selections: list[ExtractionSelection],
        candidates: list[ExtractionCandidate],
        allowed_candidate_ids: set[str],
        knowledge: StructuredKnowledge,
        selected_ids: set[str],
        heading_counts: dict[str, int],
        maximum: int | None,
        role_question: bool,
        exhaustive: bool,
        evidence_requirement: EvidenceRequirement,
    ) -> None:
        """Accept valid, grounded, authorized LLM selections."""

        candidate_map = {
            candidate.candidate_id: candidate
            for candidate in candidates
        }

        for selection in selections:
            candidate_id = selection["candidate_id"]

            if candidate_id not in candidate_map:
                continue

            if candidate_id not in allowed_candidate_ids:
                continue

            if candidate_id in selected_ids:
                continue

            candidate = candidate_map[candidate_id]

            heading = self._candidate_heading(candidate)

            current_count = heading_counts.get(
                heading,
                0,
            )

            if (
                maximum is not None
                and current_count >= maximum
            ):
                continue

            if exhaustive and not self._has_required_structural_evidence(
                candidate=candidate,
                evidence_requirement=evidence_requirement,
            ):
                continue

            if self._is_ambiguous_candidate(
                candidate=candidate,
                candidates=candidates,
            ):
                continue

            if not self.source_quote_validator.is_supported(
                source_quote=candidate.source_quote,
                source_text=candidate.source_text,
            ):
                continue

            value = (
                candidate.heading
                if role_question
                else candidate.source_quote
            )

            fact = self._create_fact(
                candidate=candidate,
                confidence=selection["confidence"],
                value=value,
            )

            if self._is_duplicate(
                fact=fact,
                knowledge=knowledge,
            ):
                continue

            knowledge.facts.append(fact)

            selected_ids.add(candidate_id)

            heading_counts[heading] = (
                current_count + 1
            )

    def _complete_exhaustive_selection(
        self,
        candidates: list[ExtractionCandidate],
        selections: list[ExtractionSelection],
        candidate_map: dict[str, ExtractionCandidate],
        evidence_requirement: EvidenceRequirement,
        relationship_question: bool,
        role_question: bool,
        max_per_heading: int | None,
        facts: list[KnowledgeFact],
        selected_ids: set[str],
        heading_counts: dict[str, int],
    ) -> None:
        """Complete exhaustive extraction without trusting the LLM for coverage."""

        headings: list[str] = []

        for candidate in candidates:
            heading = self._candidate_heading(candidate)

            if heading not in headings:
                headings.append(heading)

        for heading in headings:
            current_count = heading_counts.get(
                heading,
                0,
            )

            heading_candidates = [
                candidate
                for candidate in candidates
                if self._candidate_heading(candidate) == heading
            ]

            for candidate in heading_candidates:
                if (
                    max_per_heading is not None
                    and current_count >= max_per_heading
                ):
                    break

                if candidate.candidate_id in selected_ids:
                    continue

                if not self._has_required_structural_evidence(
                    candidate=candidate,
                    evidence_requirement=evidence_requirement,
                ):
                    continue

                if self._is_ambiguous_candidate(
                    candidate=candidate,
                    candidates=candidates,
                ):
                    continue

                if not self.source_quote_validator.is_supported(
                    source_quote=candidate.source_quote,
                    source_text=candidate.source_text,
                ):
                    continue

                value = (
                    candidate.heading
                    if role_question
                    else candidate.source_quote
                )

                fact = self._create_fact(
                    candidate=candidate,
                    confidence=1.0,
                    value=value,
                )

                if self._is_duplicate(
                    fact=fact,
                    knowledge=StructuredKnowledge(
                        facts=facts
                    ),
                ):
                    selected_ids.add(
                        candidate.candidate_id
                    )
                    continue

                facts.append(fact)

                selected_ids.add(
                    candidate.candidate_id
                )

                current_count += 1

            heading_counts[heading] = current_count

    def _select_exhaustive_representative(
        self,
        candidates: list[ExtractionCandidate],
        evidence_requirement,
    ) -> ExtractionCandidate | None:
        """Select the strongest evidence-bearing candidate for a structural group."""

        eligible = [
            candidate
            for candidate in candidates
            if self._has_required_structural_evidence(
                candidate=candidate,
                evidence_requirement=evidence_requirement,
            )
        ]

        if not eligible:
            return None

        return eligible[0]

    def _has_required_structural_evidence(
        self,
        candidate: ExtractionCandidate,
        evidence_requirement,
    ) -> bool:
        """Return whether a candidate contains the structural evidence required by the question."""

        if not evidence_requirement.structural_value_required:
            return True

        heading = " ".join(
            candidate.heading.split()
        ).strip()

        structural_context = " ".join(
            candidate.structural_context.split()
        ).strip()

        if not heading and not structural_context:
            return False

        return True

    def _candidate_heading(
        self,
        candidate: ExtractionCandidate,
    ) -> str:
        """Return the source-owned heading for a candidate."""

        return candidate.heading

    def _is_ambiguous_candidate(
        self,
        candidate: ExtractionCandidate,
        candidates: list[ExtractionCandidate],
    ) -> bool:
        """Return whether identical evidence has multiple source locations."""

        matches = [
            other
            for other in candidates
            if (
                other.source_quote == candidate.source_quote
                and (
                    other.source != candidate.source
                    or (
                        other.source == candidate.source
                        and other.page_number != candidate.page_number
                    )
                )
            )
        ]

        return bool(matches)

    def _is_duplicate(
        self,
        fact: KnowledgeFact,
        knowledge: StructuredKnowledge,
    ) -> bool:
        """Return whether the fact is already present."""

        return any(
            existing.value == fact.value
            and existing.source == fact.source
            and existing.page_number == fact.page_number
            for existing in knowledge.facts
        )

    def _create_fact(
        self,
        candidate: ExtractionCandidate,
        confidence: float,
        value: str = "",
    ) -> KnowledgeFact:
        """Create a source-owned knowledge fact."""

        resolved_value = (
            value
            if value
            else candidate.source_quote
        )

        return KnowledgeFact(
            name=self._candidate_heading(candidate),
            value=resolved_value,
            source=candidate.source,
            page_number=candidate.page_number,
            confidence=confidence,
        )

    def _reject(
        self,
        candidate: ExtractionCandidate,
        confidence: float,
    ) -> None:
        """Record a rejected candidate for diagnostics."""

        fact = KnowledgeFact(
            name=self._candidate_heading(candidate),
            value=candidate.source_quote,
            source=candidate.source,
            page_number=candidate.page_number,
            confidence=confidence,
        )

        self.execution_debugger.rejected_fact(fact)