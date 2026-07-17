# Project Niyam - System Overview

## Purpose

Project Niyam is an AI-powered enterprise knowledge assistant built using
Retrieval Augmented Generation (RAG).

Its objective is to answer user questions using trusted enterprise
documents instead of relying solely on the Language Model's knowledge.

The system separates document ingestion, retrieval, prompt engineering,
and LLM interaction into independent components to achieve a modular,
maintainable, and extensible architecture.

---

# High Level Architecture

```
                        User
                          │
                          ▼
                     Application
                          │
          ┌───────────────┴────────────────┐
          ▼                                ▼
  Retrieval Pipeline                Generation Pipeline
          │                                │
          ▼                                ▼
 Retrieval Service               Prompt Builder
          │                                │
          ▼                                ▼
 Embedding Service               Ollama Service
          │                                │
          ▼                                ▼
 Vector Repository               Large Language Model
          │                                │
          └───────────────┬────────────────┘
                          ▼
                    Answer Result
```

---

# Two Independent Pipelines

Project Niyam consists of two major pipelines.

## 1. Ingestion Pipeline

Runs whenever a new document is added.

Responsibilities:

- Read documents
- Split documents into chunks
- Generate vector embeddings
- Store chunks in the vector database

This pipeline is executed once for each document.

---

## 2. Retrieval Pipeline

Runs for every user question.

Responsibilities:

- Convert the question into an embedding
- Search the vector database
- Retrieve relevant knowledge
- Build a prompt
- Ask the LLM
- Return the final answer

---

# Design Principles

Project Niyam follows several architectural principles.

## Single Responsibility

Each class performs one well-defined responsibility.

Examples:

- PDFReader reads PDFs.
- TextChunker creates chunks.
- EmbeddingService generates embeddings.
- VectorRepository communicates with ChromaDB.
- PromptBuilder creates prompts.
- OllamaService communicates with the Language Model.

---

## Separation of Concerns

Business logic is separated from infrastructure.

Examples:

- Retrieval logic does not know about Ollama.
- Prompt engineering does not know about ChromaDB.
- VectorRepository does not know about prompt construction.

---

## Composition Root

Application.py acts as the Composition Root.

It is responsible for constructing and wiring together all application
services.

No other class is responsible for creating dependencies.

---

## Observability

Project Niyam provides visibility into every major stage of the pipeline.

Current inspectors include:

- Retrieval Inspector
- Prompt Inspector

Inspectors never modify application behavior.

They exist only to improve debugging and understanding.

---

## Extensibility

The architecture is designed to support future enhancements without major
refactoring.

Examples include:

- Multiple LLM providers
- Hybrid Search
- Conversation Memory
- Re-ranking
- Source Attribution
- Multi-document Retrieval
- Agentic Workflows

---

# Current Technology Stack

Language

- Python

LLM

- Ollama
- Qwen 2.5

Vector Database

- ChromaDB

Embedding Model

- Ollama Embeddings

Document Reader

- PyPDF

Architecture Style

- Layered Architecture
- Service-Oriented Design
- Retrieval Augmented Generation (RAG)

---

# Current Project Status

Completed

- Document ingestion
- PDF parsing
- Chunk generation
- Embedding generation
- Vector storage
- Semantic retrieval
- Prompt engineering
- LLM integration
- Retrieval observability
- Prompt observability

Upcoming

- Source Attribution
- Conversation Memory
- Hybrid Search
- Re-ranking
- Multi-document support