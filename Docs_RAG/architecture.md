# System Architecture: Dietary Guidance RAG Chatbot

This document outlines the detailed system architecture for the Dietary Guidance RAG (Retrieval-Augmented Generation) Chatbot, based on the requirements defined in the `problemStatement.md`.

## 1. High-Level Architecture Overview

The system is composed of two primary pipelines:
1. **Data Ingestion Pipeline:** Processes the pre-parsed dataset (`blocks.jsonl`), chunks the data intelligently, generates vector embeddings, and stores them in a Vector Database.
2. **Query Pipeline:** Receives user questions, retrieves relevant information from the Vector Database, and uses a Large Language Model (LLM) to generate an accurately cited, constraint-bound response.

---

## 2. Data Ingestion Pipeline

### 2.1. Data Loading & Parsing
- **Input:** `blocks.jsonl` (contains logical document blocks like headings, paragraphs, and tables).
- **Process:** Iterate through the JSONL file, reading each block and its associated metadata (`document_id`, `type`, `heading_path`, `ordinal`).

### 2.2. Chunking & Assembly Strategy
Since the data is already logically separated, naive fixed-size chunking will destroy context. The assembly process involves:
- **Contextual Grouping:** Grouping related blocks together (e.g., combining a heading block with its immediate child paragraphs).
- **Table Handling:** Serializing tables (using headers and rows) into a text-readable format or markdown so the embedding model understands the relationships.
- **Metadata Attachment:** Every finalized chunk must retain a metadata payload containing:
  - `document_id`: The source document.
  - `heading_path`: The hierarchical location of the chunk.
  - `chunk_text`: The actual assembled text.

### 2.3. Embedding Generation
- Pass the assembled `chunk_text` through an Embedding Model (e.g., OpenAI `text-embedding-3-small`, HuggingFace sentence transformers, etc.) to generate dense vector representations.

### 2.4. Vector Database
- **Storage:** A Vector Database (e.g., ChromaDB, Pinecone, FAISS with metadata support, or Qdrant) is used to store the embeddings.
- **Requirement:** The database must support **metadata filtering**, allowing the system to restrict searches to a specific `document_id` if required.

---

## 3. Query & Retrieval Pipeline

### 3.1. Query Processing
- The user submits a query (e.g., *"How long can I keep chicken in the fridge?"*).
- An optional preprocessing step can detect if the user is asking about a specific document.

### 3.2. Vector Search
- The user's query is embedded using the same Embedding Model from the ingestion phase.
- A similarity search (e.g., cosine similarity) is performed against the Vector Database to retrieve the top-*k* most relevant chunks.
- If the user specified a source, metadata filters (e.g., `where document_id == 'cold-food-storage'`) are applied.

---

## 4. Answer & Generation Layer (LLM)

This is the core logic that ensures constraints and strict citation requirements are met.

### 4.1. Prompt Engineering & Constraints
The retrieved chunks and their metadata are formatted and injected into the LLM context prompt. The system prompt enforces strict rules:
1. **Strict Adherence:** Answer *only* using the provided context chunks. Do not use external knowledge.
2. **Citation Requirement:** Every claim must end with a citation referencing the `document_id` and the `heading_path` from which it was derived.
3. **Cross-Document Separation:** If the context contains multiple distinct `document_id`s addressing the same topic, the LLM must answer per document separately (e.g., *"According to [Doc A]... However, [Doc B] states..."*). Do not blend them into a single claim.

### 4.2. Handling Refusals (Guardrails)
The prompt and post-processing logic must handle two specific refusal scenarios:
1. **Not in Corpus:** 
   - *Condition:* The retrieved chunks do not contain the answer.
   - *Action:* The LLM explicitly states that the guidance does not cover the question and lists the `document_id`s that were searched.
2. **Out of Scope (By Design):**
   - *Condition:* The user asks for medical advice, calorie counting, or weight targets.
   - *Action:* The system hard-declines the request and advises the user to seek a qualified medical professional. This can be handled via prompt instructions or a separate lightweight classification model acting as a guardrail before retrieval.

---

## 5. Technology Stack Recommendations

- **Data Processing:** Python (Pandas/JSON libraries)
- **Embeddings:** OpenAI Embeddings or open-source HuggingFace models (e.g., `all-MiniLM-L6-v2`).
- **Vector Store:** ChromaDB (excellent for local prototyping with metadata filtering) or Pinecone.
- **LLM:** GPT-4o-mini, Claude 3 Haiku, or Llama 3 (for fast, constrained generation).
- **Framework:** LangChain or LlamaIndex to orchestrate the retrieval and prompt formatting easily.
- **User Interface:** Streamlit or Gradio for a rapid, interactive chatbot prototype.
