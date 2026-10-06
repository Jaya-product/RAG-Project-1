import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from retriever import retrieve_chunks, format_context

# Load environment variables (GROQ_API_KEY)
load_dotenv()

# The system prompt enforcing our RAG constraints
SYSTEM_PROMPT = """You are a helpful dietary guidance assistant. You will be provided with context retrieved from official public guidance documents.

Your strict rules:
1. **Answer ONLY based on the provided context.** Do not use outside knowledge.
2. **Context Headers:** The context is provided in chunks with headers formatted as `[Source Document: <doc_id> | Section: <path>]`. 
3. **Citations:** You MUST append an explicit citation using the exact `Source Document` and `Section` to every claim you make. (e.g., "According to [Source Document: who-healthy-diet | Section: KEY FACTS], total fat should not exceed 30%...").
4. **Missing Info:** If the context does not contain the answer to the user's question, you must explicitly say: "I'm sorry, but the provided documents do not contain the answer to this question." and list the Source Documents that were searched.
5. **Out of Scope Guardrails:** You must politely refuse to answer any questions asking for specific medical advice, calorie counting for specific foods, or personal weight loss targets, stating that this is outside your scope.
6. **Cross-Document Formatting:** If the context contains multiple different source documents, synthesize the answer by separating the sources (e.g., "According to document X... On the other hand, document Y states...").

CONTEXT:
{context}
"""

def generate_response(query: str, document_id: str = None) -> str:
    """
    Retrieves context for the query, builds the prompt, and calls the Groq LLM.
    """
    # 1. Retrieve and format the context
    retrieved_results = retrieve_chunks(query, top_k=3, document_id=document_id)
    formatted_context = format_context(retrieved_results)
    
    # 2. Build the prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "{query}")
    ])
    
    prompt = prompt_template.format_messages(
        context=formatted_context,
        query=query
    )
    
    # 3. Initialize LLM using the user's requested model
    llm = ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0.0
    )
    
    # 4. Generate Response
    response = llm.invoke(prompt)
    
    return response.content

if __name__ == "__main__":
    # Ensure API key is present
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY is not set in your .env file!")
        print("Please add it to .env before running this script.")
        exit(1)
        
    print("Testing Phase 5: LLM Logic...\n")
    
    # Test 1: Valid question within context
    test_query_1 = "What should I avoid eating if I want to reduce sugar?"
    print(f"--- Test 1 (In-Context Query) ---\nQuery: {test_query_1}")
    print("Generating response...")
    print("\nResponse:")
    print(generate_response(test_query_1))
    print("\n" + "="*50 + "\n")
    
    # Test 2: Out of scope guardrail test
    test_query_2 = "Can you give me medical advice for my diabetes?"
    print(f"--- Test 2 (Guardrail Test) ---\nQuery: {test_query_2}")
    print("Generating response...")
    print("\nResponse:")
    print(generate_response(test_query_2))
