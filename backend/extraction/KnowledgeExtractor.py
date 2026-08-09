"""
Knowledge Extractor.

Type:
    Domain Service

Purpose:
    Extract structured knowledge from retrieved context.

Responsibilities:
    - Build the extraction prompt.
    - Invoke the LLM.
    - Parse extracted JSON.
    - Split compound facts into atomic facts.
    - Validate extracted facts against retrieved context.
    - Produce StructuredKnowledge.

Does NOT:
    - Retrieve knowledge.
    - Answer user questions.
    - Perform reasoning.
"""

from __future__ import annotations

import json
import re
from typing import cast

from backend.diagnostic.ExecutionDebugger import ExecutionDebugger
from backend.extraction.ExtractionPromptBuilder import ExtractionPromptBuilder
from backend.extraction.KnowledgeFact import KnowledgeFact
from backend.extraction.KnowledgeFactJson import KnowledgeFactJson
from backend.extraction.KnowledgeSchema import KnowledgeSchema
from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.llm.Message import Messages
from backend.llm.OllamaService import OllamaService
from backend.retrieval.KnowledgeNode import KnowledgeNode


class KnowledgeExtractor:
    """Extracts structured knowledge from retrieved context."""

    prompt_builder: ExtractionPromptBuilder
    ollama_service: OllamaService
    execution_debugger: ExecutionDebugger
    knowledge_schema: KnowledgeSchema

    def __init__(
        self,
        prompt_builder: ExtractionPromptBuilder,
        ollama_service: OllamaService,
        execution_debugger: ExecutionDebugger,
        knowledge_schema: KnowledgeSchema,
    ) -> None:
        """Initialize the knowledge extractor."""

        self.prompt_builder = prompt_builder
        self.ollama_service = ollama_service
        self.execution_debugger = execution_debugger
        self.knowledge_schema = knowledge_schema

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def extract(
        self,
        question: str,
        knowledge_nodes: list[KnowledgeNode],
    ) -> StructuredKnowledge:
        """Extract only facts grounded in retrieved context."""

        messages: Messages = self.prompt_builder.build(
            question=question,
            knowledge_nodes=knowledge_nodes,
        )

        self.execution_debugger.prompt(
            messages
        )

        response = self.ollama_service.generate(
            messages=messages,
            response_format=self.knowledge_schema.json_schema(),
        )

        self.execution_debugger.raw_llm_response(
            title="Knowledge Extraction",
            response=response,
        )

        structured_knowledge = self._parse(
            response=response,
            knowledge_nodes=knowledge_nodes,
        )

        self.execution_debugger.extraction(
            structured_knowledge
        )

        return structured_knowledge

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse(
        self,
        response: str,
        knowledge_nodes: list[KnowledgeNode],
    ) -> StructuredKnowledge:
        """Parse, split, and validate extracted knowledge."""

        cleaned_response = self._clean_response(
            response
        )

        data = cast(
            list[KnowledgeFactJson],
            json.loads(cleaned_response),
        )

        structured_knowledge = StructuredKnowledge()

        for item in data:

            name = item["name"]
            source_quote = item["source_quote"]
            confidence = float(
                item.get("confidence", 1.0)
            )

            atomic_quotes = self._split_into_atomic_facts(
                source_quote
            )

            for atomic_quote in atomic_quotes:

                candidate = self._find_supporting_node(
                    name=name,
                    value=atomic_quote,
                    knowledge_nodes=knowledge_nodes,
                )

                if candidate is None:
                    self.execution_debugger.rejected_fact(
                        KnowledgeFact(
                            name=name,
                            value=atomic_quote,
                            source="",
                            page_number=0,
                            confidence=confidence,
                        )
                    )
                    continue

                fact = KnowledgeFact(
                    name=name,
                    value=atomic_quote,
                    source=candidate.metadata.source,
                    page_number=candidate.metadata.page_number,
                    confidence=confidence,
                )

                if self._is_duplicate(
                    fact=fact,
                    knowledge=structured_knowledge,
                ):
                    continue

                structured_knowledge.facts.append(
                    fact
                )

        return structured_knowledge

    # ------------------------------------------------------------------
    # Atomic Fact Handling
    # ------------------------------------------------------------------

    def _split_into_atomic_facts(
        self,
        source_quote: str,
    ) -> list[str]:
        """Split a compound source quote into conservative atomic facts."""

        normalized_quote = re.sub(
            r"\s+",
            " ",
            source_quote,
        ).strip()

        if not normalized_quote:
            return []

        sentences = self._split_sentences(
            normalized_quote
        )

        atomic_facts: list[str] = []

        for sentence in sentences:

            clauses = self._split_independent_clauses(
                sentence
            )

            atomic_facts.extend(
                clause
                for clause in clauses
                if clause.strip()
            )

        return atomic_facts

    def _split_sentences(
        self,
        text: str,
    ) -> list[str]:
        """Split text into sentence-level facts."""

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def _split_independent_clauses(
        self,
        sentence: str,
    ) -> list[str]:
        """Split independently stated claims joined by conjunctions."""

        pattern = (
            r"\s+and\s+"
            r"(?="
            r"(?:"
            r"built\b"
            r"|led\b"
            r"|reduced\b"
            r"|launched\b"
            r"|delivered\b"
            r"|enabled\b"
            r"|improved\b"
            r"|increased\b"
            r"|decreased\b"
            r"|created\b"
            r"|developed\b"
            r"|filed\b"
            r"|earned\b"
            r"|achieved\b"
            r"|\d"
            r")"
            r")"
        )

        clauses = re.split(
            pattern,
            sentence,
            flags=re.IGNORECASE,
        )

        return [
            clause.strip()
            for clause in clauses
            if clause.strip()
        ]


    # ------------------------------------------------------------------
    # Grounding
    # ------------------------------------------------------------------

    def _find_supporting_node(
        self,
        name: str,
        value: str,
        knowledge_nodes: list[KnowledgeNode],
    ) -> KnowledgeNode | None:
        """Find a retrieved node where name and fact are locally supported."""

        for node in knowledge_nodes:

            if not self._name_is_supported(
                name=name,
                source_text=node.content,
            ):
                continue

            if not self._value_is_supported(
                value=value,
                source_text=node.content,
            ):
                continue

            if not self._facts_are_locally_associated(
                name=name,
                value=value,
                source_text=node.content,
            ):
                continue

            return node

        return None

    def _facts_are_locally_associated(
        self,
        name: str,
        value: str,
        source_text: str,
    ) -> bool:
        """Verify that the name and fact occur within the same local section."""

        normalized_source = re.sub(
            r"\s+",
            " ",
            source_text.lower(),
        )

        normalized_name = re.sub(
            r"\s+",
            " ",
            name.lower(),
        ).strip()

        normalized_value = re.sub(
            r"\s+",
            " ",
            value.lower(),
        ).strip()

        name_position = normalized_source.find(
            normalized_name
        )

        if name_position == -1:
            return False

        value_position = normalized_source.find(
            normalized_value
        )

        if value_position == -1:
            return False

        distance = abs(
            value_position - name_position
        )

        return distance <= 500

    def _name_is_supported(
        self,
        name: str,
        source_text: str,
    ) -> bool:
        """Verify that the extracted name appears in source text."""

        name_tokens = self._tokens(
            name
        )

        source_tokens = self._tokens(
            source_text
        )

        if not name_tokens:
            return False

        matched_tokens = sum(
            1
            for token in name_tokens
            if token in source_tokens
        )

        coverage = (
            matched_tokens / len(name_tokens)
        )

        return coverage >= 0.80

    def _value_is_supported(
        self,
        value: str,
        source_text: str,
    ) -> bool:
        """Verify that the extracted fact is supported by source text."""

        value_tokens = self._tokens(
            value
        )

        source_tokens = self._tokens(
            source_text
        )

        if not value_tokens:
            return False

        matched_tokens = sum(
            1
            for token in value_tokens
            if token in source_tokens
        )

        coverage = (
            matched_tokens / len(value_tokens)
        )

        return coverage >= 0.85

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _clean_response(
        self,
        response: str,
    ) -> str:
        """Remove optional markdown fences from an LLM response."""

        cleaned_response = response.strip()

        if not cleaned_response.startswith("```"):
            return cleaned_response

        lines = cleaned_response.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines).strip()

    def _tokens(
        self,
        text: str,
    ) -> set[str]:
        """Normalize text into comparison tokens."""

        return set(
            re.findall(
                r"[a-z0-9]+",
                text.lower(),
            )
        )

    def _is_duplicate(
        self,
        fact: KnowledgeFact,
        knowledge: StructuredKnowledge,
    ) -> bool:
        """Check whether an equivalent fact was already extracted."""

        return any(
            existing.name == fact.name
            and existing.value == fact.value
            and existing.source == fact.source
            and existing.page_number == fact.page_number
            for existing in knowledge.facts
        )