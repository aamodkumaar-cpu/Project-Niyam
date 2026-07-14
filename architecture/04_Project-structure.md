# Project Niyam - Project Structure

## Purpose

A well-organized project allows developers to quickly locate existing code
and confidently decide where new classes should be created.

Project Niyam organizes code based on **responsibility**, not based on
technology or implementation details.

Each package represents a logical part of the system.

---

# Current Project Structure

```
backend/

├── app.py
├── application.py

├── config/
├── ingestion/
├── retrieval/
├── llm/
├── prompt/
├── diagnostics/
├── results/
├── documents/
```

---

# application.py

Purpose

Acts as the **Composition Root**.

Responsibilities

- Creates application services
- Wires dependencies together
- Coordinates the complete workflow

Should NOT contain

- Business logic
- Retrieval logic
- Prompt engineering
- Database operations

---

# config/

Purpose

Contains all application configuration.

Examples

- Model names
- Database paths
- Document locations
- Debug flags

Typical Classes

- settings.py

Rule

If a value can change between environments, it belongs here.

---

# ingestion/

Purpose

Responsible for converting documents into searchable knowledge.

Contains

- IngestionService
- PDFReader
- TextChunker
- EmbeddingService
- Page
- Chunk

Rule

Everything related to document ingestion belongs here.

Nothing in this package should know about the Language Model.

---

# retrieval/

Purpose

Responsible for finding relevant knowledge.

Contains

- RetrievalService
- VectorRepository
- KnowledgeNode
- DocumentMetadata

Rule

Everything related to semantic search belongs here.

Nothing here should communicate with the LLM.

---

# prompt/

Purpose

Responsible for Prompt Engineering.

Contains

- PromptBuilder

Responsibilities

- Build chat messages
- Format retrieved knowledge
- Combine context with user questions

Rule

PromptBuilder prepares information.

It does not send anything to the Language Model.

---

# llm/

Purpose

Responsible for communicating with Language Models.

Contains

- OllamaService

Future

- OpenAIService
- GeminiService
- ClaudeService

Rule

Every Language Model implementation belongs here.

These classes should know nothing about retrieval or prompt engineering.

---

# diagnostics/

Purpose

Provides visibility into system execution.

Current Classes

- RetrievalInspector
- PromptInspector

Future Classes

- TimingInspector
- TokenInspector
- PipelineInspector

Rule

Diagnostics never change application behavior.

They only display information.

---

# results/

Purpose

Represents responses returned by the application.

Current Classes

- AnswerResult

Future Classes

- SearchResult
- Citation
- RetrievalMetrics

Rule

These classes are returned to callers.

They are not responsible for generating data.

---

# documents/

Purpose

Stores documents that will be ingested.

Examples

- PDF files
- Word documents
- Text files

Rule

No Python code should exist here.

---

# Why We Don't Have a utils/ Folder

Many projects gradually accumulate a large utils/ folder containing
unrelated helper functions.

Examples

```
utils/

pdf.py
string.py
logger.py
date.py
file.py
misc.py
```

Over time, the folder becomes difficult to navigate because it groups
classes by convenience rather than responsibility.

Project Niyam avoids this pattern.

Instead, each class is placed in the package that best reflects its
business responsibility.

Examples

PDFReader

→ ingestion/

PromptBuilder

→ prompt/

VectorRepository

→ retrieval/

This makes the project easier to understand and maintain.

---

# How to Decide Where a New Class Belongs

Ask one simple question.

"What is this class responsible for?"

Examples

Reads PDFs?

→ ingestion/

Builds prompts?

→ prompt/

Calls the LLM?

→ llm/

Stores vectors?

→ retrieval/

Displays debugging information?

→ diagnostics/

Returns data to callers?

→ results/

If the answer is unclear, the class probably has more than one
responsibility and should be split.

---

# Guiding Principle

Project Niyam organizes code by **business responsibility**, not by
technical implementation.

This keeps the architecture intuitive, maintainable, and easy to extend
as the project evolves.