# Project Niyam - Design Principles

## Purpose

This document defines the architectural principles followed while building
Project Niyam.

These principles guide every design decision and help keep the system
simple, maintainable, extensible and easy to understand.

Whenever a new feature is introduced, it should follow these principles.

---

# Principle 1

## Single Responsibility Principle

Every class should have one well-defined responsibility.

A class should do one thing and do it well.

Examples

✓ PDFReader --- Reads PDF documents.

✓ TextChunker --- Creates chunks.

✓ EmbeddingService --- Generates embeddings.

✓ PromptBuilder --- Builds prompts.

✗ Avoid classes that

- Read PDFs
- Generate embeddings
- Store vectors

at the same time.

---

# Principle 2

## Separation of Concerns

Each layer of the application should focus on one concern.

Examples

Retrieval --- Responsible only for finding knowledge.
Prompt --- Responsible only for prompt engineering.
LLM --- Responsible only for communicating with the language model.
Diagnostics --- Responsible only for observability.

Business responsibilities should never overlap.

---

# Principle 3

## Composition Root

Application.py is the Composition Root.

Its responsibilities are

- Create services
- Wire dependencies
- Coordinate workflows

No other class should instantiate application services.

---

# Principle 4

## Dependency Direction

Higher-level components depend on abstractions and services.

Lower-level components never control higher-level workflows.

Example

Application
↓
RetrievalService
↓
VectorRepository

Application controls the flow.

Repositories never call Application.

---

# Principle 5

## Strong Domain Objects

Business data should be represented using dedicated classes.

Examples

Page

Chunk

KnowledgeNode

DocumentMetadata

AnswerResult

Avoid passing dictionaries throughout the application.

Dedicated objects improve

- readability
- type safety
- maintainability

---

# Principle 6

## Infrastructure Isolation

External libraries should be hidden behind dedicated services.

Examples

Ollama
↓
OllamaService
ChromaDB
↓
VectorRepository
PyPDF
↓
PDFReader

If an external library changes, only one class should require modification.

---

# Principle 7

## Observability

Every important stage should be observable.

Current inspectors

- RetrievalInspector
- PromptInspector

Future inspectors

- TimingInspector
- TokenInspector
- PipelineInspector

Inspectors must never modify application behaviour.

They exist only for visibility.

---

# Principle 8

## Explicit Naming

Prefer descriptive names over abbreviations.

Examples

EmbeddingService instead of EmbedSvc
VectorRepository instead of VectorDB
PromptBuilder instead of PromptUtil

Readable code is more valuable than shorter code.

---

# Principle 9

## Configuration over Hardcoding

Configuration belongs in config/settings.py

Examples

- Model names
- Database paths
- Chunk size
- Top K
- Debug flags

Business logic should never contain hardcoded configuration values.

---

# Principle 10

## Build for Extension

New capabilities should require minimal modification to existing code.

Examples

Future additions

- Hybrid Search
- Multiple LLMs
- Conversation Memory
- Source Attribution
- Re-ranking

should extend the architecture rather than replace it.

---

# Principle 11

## Prefer Composition over Inheritance

Project Niyam favors composition.

Example

Application owns

- RetrievalService
- PromptBuilder
- OllamaService

instead of creating deep inheritance hierarchies.

Composition produces simpler and more flexible designs.

---

# Principle 12

## Keep Components Loosely Coupled

Each component should know only what it needs.

Examples

PromptBuilder - does not know

- ChromaDB
- Ollama
- Embeddings

VectorRepository - does not know
- Prompt Engineering
- LLM
- User Interface

Loose coupling simplifies testing and future evolution.

---

# Principle 13

## Incremental Development

Large architectural changes should be implemented as a series of small,
verifiable steps.

Preferred workflow

Design
↓
Implement
↓
Run
↓
Verify
↓
Commit
↓

Repeat

Small iterations reduce bugs and simplify debugging.

---

# Principle 14

## Document Architectural Decisions

Architecture is as important as code.

Important decisions should be documented.

Examples

- Why PromptBuilder is separate from OllamaService.
- Why AnswerResult exists.
- Why utils/ is intentionally avoided.
- Why inspectors never modify execution.

Future developers should understand not only what the system does,
but why it was designed this way.

---

# Principle 15

## Simplicity First

Choose the simplest design that satisfies today's requirements while
allowing reasonable future growth.

Avoid adding abstractions before they are needed.

A simple architecture that evolves gradually is preferred over an
over-engineered design.

---

# Final Principle

## Every Class Must Be Able to Explain Its Existence

Every class should answer three questions.

Why do I exist?

What am I responsible for?

What am I intentionally NOT responsible for?

Every Project Niyam class begins with a documentation block describing
these answers.

This ensures that responsibilities remain clear as the project grows.