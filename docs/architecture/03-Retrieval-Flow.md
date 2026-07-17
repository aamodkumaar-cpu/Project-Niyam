# Project Niyam - Retrieval Pipeline

## Purpose

The Retrieval Pipeline is responsible for answering user questions using
knowledge previously stored in the Vector Database.

Unlike the ingestion pipeline, which runs only once per document, the
retrieval pipeline executes for every user question.

Its objective is to retrieve the most relevant knowledge and provide that
knowledge to the Language Model for answer generation.

---

# High-Level Flow

                     User Question
                           │
                           ▼
                     Application
                           │
                           ▼
                  RetrievalService
                           │
                           ▼
                 EmbeddingService
                           │
        Converts Question → Vector
                           │
                           ▼
                  VectorRepository
                           │
      Searches Similar Knowledge Chunks
                           │
                           ▼
                  KnowledgeNode List
                           │
                           ▼
                RetrievalInspector
                           │
             Displays Retrieved Chunks
                           │
                           ▼
                    PromptBuilder
                           │
      Converts Knowledge → Chat Messages
                           │
                           ▼
                 PromptInspector
                           │
          Displays Final Prompt
                           │
                           ▼
                   OllamaService
                           │
      Sends Messages to the LLM
                           │
                           ▼
                    AnswerResult
                           │
                           ▼
                     Final Answer

---

# Step-by-Step Flow

## Step 1

### User asks a question

Example

"What companies has Amod worked with?"

Application receives the question.

Application itself does not retrieve documents or call the LLM.

Its responsibility is to coordinate the complete workflow.

---

## Step 2

### RetrievalService

Responsibility

Coordinates the retrieval workflow.

It performs two tasks.

1. Convert the question into an embedding.

2. Search the Vector Database.

It delegates both responsibilities to dedicated components.

---

## Step 3

### EmbeddingService

Responsibility

Converts the user's question into a vector embedding.

Input

Question

Example

"What companies has Amod worked with?"

Output

Question Embedding

This embedding represents the semantic meaning of the question rather than
its exact words.

---

## Step 4

### VectorRepository

Responsibility

Searches ChromaDB for the most similar embeddings.

Input

Question Embedding

Output

KnowledgeNode objects.

Each KnowledgeNode contains

- Chunk Content
- Similarity Score
- Document Metadata

---

## Step 5

### RetrievalInspector

Responsibility

Displays retrieved knowledge.

Information displayed

- Ranking
- Similarity Score
- Page Number
- Chunk Number
- Preview

Purpose

Provides observability into retrieval quality.

It never modifies retrieval results.

---

## Step 6

### PromptBuilder

Responsibility

Builds chat messages for the Language Model.

Input

- User Question
- Knowledge Nodes

Output

Messages

The PromptBuilder combines

- Instructions
- Retrieved Context
- User Question

into structured chat messages.

---

## Step 7

### PromptInspector

Responsibility

Displays the exact messages that will be sent to the LLM.

Purpose

Allows prompt debugging.

Helps understand why the LLM produced a particular answer.

---

## Step 8

### OllamaService

Responsibility

Communicates with the Language Model.

Input

Chat Messages

Output

Generated Answer

OllamaService knows nothing about

- Retrieval
- ChromaDB
- Prompt Engineering

Its only responsibility is communicating with the LLM.

---

## Step 9

### AnswerResult

Responsibility

Represents the final output returned by the application.

Current Contents

- Generated Answer
- Sources

Future versions may also include

- Confidence Score
- Model Used
- Token Usage
- Processing Time
- Retrieved Chunks

---

# Data Flow

Question

↓

Question Embedding

↓

Knowledge Nodes

↓

Chat Messages

↓

LLM Response

↓

Answer Result

---

# Classes Involved

| Class | Responsibility |
|--------|----------------|
| Application | Coordinates retrieval pipeline |
| RetrievalService | Controls retrieval |
| EmbeddingService | Converts question into embedding |
| VectorRepository | Searches ChromaDB |
| RetrievalInspector | Displays retrieved chunks |
| PromptBuilder | Builds LLM messages |
| PromptInspector | Displays messages |
| OllamaService | Calls the LLM |
| AnswerResult | Final application response |

---

# Why KnowledgeNode?

Instead of returning raw ChromaDB dictionaries, Project Niyam converts
database results into KnowledgeNode objects.

Benefits

- Strong typing
- Cleaner code
- Database independence
- Easier testing
- Easier future extensions

KnowledgeNode represents business knowledge rather than database records.

---

# Why AnswerResult?

Instead of returning a simple string, Project Niyam returns an AnswerResult.

Benefits

- Extensible
- Can include citations
- Can include confidence
- Can include execution metrics
- Cleaner application interface

As the project evolves, new information can be added without changing the
Application API.

---

# Design Principles

The retrieval pipeline follows these principles.

## Separation of Concerns

Each class performs one responsibility.

No class performs retrieval, prompt engineering, and LLM communication together.

---

## Observability

Every important stage can be inspected.

Current inspectors

- Retrieval Inspector
- Prompt Inspector

This dramatically simplifies debugging.

---

## Extensibility

Future improvements such as

- Hybrid Search
- Re-ranking
- Conversation Memory
- Metadata Filtering
- Multi-document Search

can be introduced with minimal architectural changes.

The retrieval pipeline has been intentionally designed for incremental evolution.