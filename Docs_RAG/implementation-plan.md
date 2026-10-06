# Phase-Wise Implementation Plan: Dietary Guidance RAG Chatbot

This document outlines a structured, phase-by-phase plan for developing the Dietary Guidance RAG Chatbot based on the requirements from `problemStatement.md` and the system design in `architecture.md`.

---

## Phase 1: Environment Setup & Foundation
**Goal:** Initialize the project repository, set up the development environment, and install necessary dependencies.

1. **Repository Setup:** Create the project structure (directories for data, scripts, UI, etc.).
2. **Environment Management:** Create a Python virtual environment (e.g., using `venv` or `conda`).
3. **Dependencies:** Install required libraries:
   - UI: `streamlit`
   - Data handling: `pandas`
   - AI/Orchestration: `langchain` (or `llama-index`), `langchain-groq`, `groq`
   - Vector Store: `chromadb` (or `pinecone-client`)
   - Embeddings: `sentence-transformers` (for local embeddings, as Groq provides the LLM, not embeddings).
4. **Environment Variables:** Set up a `.env` file to securely store API keys (e.g., `GROQ_API_KEY`).

---

## Phase 2: Data Ingestion & Chunking
**Goal:** Load the provided `blocks.jsonl` dataset and assemble the pre-parsed blocks into meaningful chunks.

1. **Data Loading:** Write a script to read and parse the `blocks.jsonl` file.
2. **Contextual Assembly (Chunking Strategy):**
   - **Grouping Logic:** Instead of using fixed-size arbitrary token chunks, the data is aggregated semantically. Blocks are grouped strictly by their `document_id` and their exact `heading_path` tuple. This ensures that a single chunk represents an entire continuous logical section of a document without breaking sentences or tables in half.
   - **Block Formatting:**
     - `paragraph` and `heading`: Kept as raw text.
     - `list_item`: Prefixed with a hyphen (`- `) to maintain list structure semantics for the embedding model.
     - `table`: Converted from JSON arrays (`header` and `rows`) into standardized Markdown tables, providing spatial context that embedding models and LLMs can parse effectively.
   - **Assembly:** The formatted text from all consecutive blocks sharing the exact same `heading_path` are concatenated with double newlines (`\n\n`) into a single `chunk_text` string.
3. **Metadata Enrichment:** Ensure every final chunk is a dictionary/object containing:
   - `chunk_text`: The assembled text/table.
   - `metadata`: A dictionary holding `document_id` and the specific `heading_path`.
4. **Documentation:** Document the chosen chunking and table-handling strategy in the project `README.md`.

---

## Phase 3: Embeddings & Vector Database Setup
**Goal:** Convert the assembled chunks into vectors and store them in a database for retrieval.

1. **Embedding Initialization:** Initialize the local HuggingFace embedding model using `sentence-transformers`. Since our chunks contain structured Markdown tables and continuous prose, we recommend using a highly capable dense retrieval model like `BAAI/bge-small-en-v1.5` or `all-MiniLM-L6-v2`.
2. **Vector Store Setup:** Initialize the local ChromaDB client (using a persistent directory like `./chroma_db`).
3. **Indexing Process:**
   - Load the `data/processed_chunks.json` file.
   - Iterate over the JSON array.
   - For each object, extract the `chunk_id`, `chunk_text`, and `metadata` (`document_id` and `heading_path`).
   - *Note:* ChromaDB requires metadata values to be strings, ints, or floats, so you will need to serialize the `heading_path` list into a single string (e.g., `" > ".join(heading_path)`).
   - Upsert the `chunk_text` into the vector database, explicitly providing the unique `chunk_id` and the formatted `metadata`.
4. **Validation:** Write a simple test script to query the database (e.g., "How long can I freeze meat?") and verify that it returns the relevant chunks along with the correct `document_id` and `heading_path`.

---

## Phase 4: Retrieval Pipeline Setup
**Goal:** Build the logic to retrieve the most relevant context based on a user's query.

1. **Basic Retrieval Logic:** Write a function (using native ChromaDB `collection.query()` or Langchain's VectorStore retriever) that takes a user query and performs a similarity search using the `BAAI/bge-small-en-v1.5` embedding model. Since our chunks are semantically aggregated and comprehensive, retrieving a smaller `top-k` (e.g., k=3 or 4) should be sufficient and keep the LLM context window clean.
2. **Metadata Filtering:** Implement logic to detect if a user is asking about a specific document. If they do, apply a ChromaDB `where` filter on the metadata (e.g., `where={"document_id": "cold-food-storage"}`).
3. **Context Formatting for Citations:** To satisfy the strict citation requirements in Phase 5, write a helper function that formats the retrieved chunks before injecting them into the LLM prompt. Each chunk must explicitly expose its metadata to the LLM. 
   - *Example format:* `[Source Document: {document_id} | Section: {heading_path}]\n{chunk_text}\n\n---`

---

## Phase 5: Answer Layer & Prompt Engineering (Core LLM Logic)
**Goal:** Connect the retrieved context to the LLM and enforce strict constraints regarding citations, refusals, and cross-document questions.

1. **System Prompt Design:** Create a robust system prompt instructing the LLM to:
   - Answer **only** based on the provided context.
   - Parse the provided context headers (formatted as `[Source Document: {document_id} | Section: {heading_path}]`).
   - Append an explicit citation using the exact `document_id` and `heading_path` to every claim made in the answer.
2. **Handling Refusals:**
   - **Not in Corpus:** Instruct the LLM to explicitly state if the context lacks the answer, and list the `document_id`s that were provided in the context.
   - **Out of Scope Guardrails:** Add explicit instructions refusing medical advice, calorie counting, or weight targets. (Alternatively, add a lightweight pre-check prompt to classify the user's query before performing retrieval).
3. **Cross-Document Formatting:** Add instructions ensuring that if the context contains multiple `document_id`s, the LLM separates the answers (e.g., "According to X... On the other hand, Y states...").
4. **Integration:** Initialize the Groq LLM (e.g., using `ChatGroq` with `openai/gpt-oss-120b` or `qwen/qwen3.6-27b`) and combine the retriever from Phase 4 with the LLM call into a single, cohesive function (`generate_response(user_query)`).

---

## Phase 6: Streamlit UI Integration
**Goal:** Build a simple interactive chatbot UI on top of the existing RAG backend without duplicating retrieval, LLM, or safety logic in the UI layer.

1. **UI Layout:** Create `ui/app.py` with the application title, description, chat interface, and a clear-chat option.
2. **Session State Management:** Use `st.session_state` to maintain chat history during the session.
3. **Chat Interface:** Use `st.chat_input()` to capture user questions and `st.chat_message()` to display user and assistant messages.
4. **Connecting the Backend:** Connect the UI to the existing Phase 5 `generate_response()` backend function.
5. **Structured Display:** Display the structured backend response, including the answer, sources/citations, and relevant safety information where applicable.
6. **Error Handling:** Add basic error handling for API failures, retrieval failures, missing configuration, and invalid backend responses.
7. **Configuration:** Keep retrieval settings such as chunk size and top-k as backend/configuration parameters rather than exposing them to the end user.

---

## Phase 7: Testing & Refinement
**Goal:** Thoroughly test the system against edge cases and refine the prompt.

1. **Accuracy Testing:** Test with standard questions (e.g., "How long can I freeze chicken?") and verify citations.
2. **Refusal Testing:** 
   - Ask an off-topic question ("Who won the World Cup?") to trigger the *Not in Corpus* refusal.
   - Ask for medical advice ("I weigh 200lbs, how many calories should I eat?") to trigger the *Out of Scope* refusal.
3. **Cross-Document Testing:** Ask a question covered by multiple documents to ensure the model separates the answers properly without blending claims.
4. **Final Review:** Ensure the `README.md` is complete with setup instructions and chunking strategy details.
