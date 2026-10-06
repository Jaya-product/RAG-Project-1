# Problem Statement: Dietary Guidance RAG Chatbot

## Brief
The goal is to build a prototype of a chatbot that answers questions about food, nutrition, and food safety. 
To ensure accuracy and reliability, a retrieval layer will be placed under the chatbot, restricting its answers strictly to official public dietary guidance documents. 
Every claim made by the chatbot must carry a citation. If the guidance does not cover a user's question, the assistant must explicitly state so.

In the final project, this will evolve into a service that answers practical queries like:
- "Is this a reasonable way to eat?"
- "How long can I keep this in the fridge?"

### The Gap
Currently, real dietary guidance exists in the form of long, careful, and often tedious PDFs published by health authorities. There is no API for this data, just written prose, resulting in low readership. This project aims to bridge that gap using Retrieval-Augmented Generation (RAG).

*Note: Nutrient numbers for individual foods are considered different data and do not belong in this system. Those will come from a structured database in Milestone 3.*

## What You Will Build

### 1. Corpus
- **Task:** The corpus is provided in `blocks.jsonl`, which contains pre-parsed content from official dietary guidance documents (e.g., WHO guidelines, food storage charts). Each line is a JSON object representing a block of text (paragraph, list item, table, etc.).
- **Requirement:** Load and parse this dataset. Extract relevant text and metadata (such as `document_id`, `type`, and `heading_path`) to serve as the foundation of your RAG system.

### 2. Chunking & Processing
- **Task:** While the data is already divided into logical blocks, you must assemble or process these blocks into meaningful chunks for vector embedding and retrieval.
- **Challenge:** You must decide how to group blocks to maintain context (e.g., should a heading be grouped with its subsequent paragraphs? How do you handle tables?).
- **Requirement:** Document your chosen chunking/assembly strategy and its trade-offs in the README. Ensure every resulting chunk carries essential context like the document ID and its hierarchical position (`heading_path`).

### 3. Retrieval
- **Task:** Build a vector index over the chunks. 
- **Capabilities:** Must support retrieval across all documents, as well as retrieval filtered to one specific named document.

### 4. Answer Layer
- **Task:** Ensure the assistant answers *only* from retrieved chunks. 
- **Requirement:** Every claim must carry a citation showing the `document_id` and the specific section (e.g., based on the `heading_path`) where the information was found.

### 5. Cross-Document Questions
- **Scenario:** Some questions might involve multiple documents (e.g., cooking oil, where both a nutrition institute and a food safety regulator have guidelines).
- **Requirement:** Answer per document, providing separate citations. **Never** blend two sources into one generalized claim about what "the guidelines say".

### 6. Refusals (Two Kinds Required)
- **Not in the corpus:** When the retrieved chunks do not contain the answer, the assistant must state that the guidance does not cover it and list what it searched.
- **Out of scope by design:** The chatbot must not provide medical advice, calorie/weight targets, or guidelines on what a person should weigh. In these cases, it must decline and point the user to a qualified professional.
