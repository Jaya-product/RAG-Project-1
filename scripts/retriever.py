import os
import chromadb
from chromadb.utils import embedding_functions

_collection = None

def get_chroma_collection():
    """Initializes and returns the ChromaDB collection. Cached for performance."""
    global _collection
    if _collection is not None:
        return _collection
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'chroma_db')
    
    client = chromadb.PersistentClient(path=db_path)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    _collection = client.get_collection(
        name="dietary_guidance",
        embedding_function=embedding_func
    )
    return _collection

def retrieve_chunks(query: str, top_k: int = 3, document_id: str = None):
    """
    Retrieves the top_k most relevant chunks for a given query.
    Optionally filters by document_id.
    """
    collection = get_chroma_collection()
    
    where_filter = None
    if document_id:
        where_filter = {"document_id": document_id}
        
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter
    )
    
    return results

def format_context(retrieved_results) -> str:
    """
    Formats the retrieved chunks from ChromaDB into a single string 
    with clear citations to inject into the LLM prompt.
    """
    if not retrieved_results or not retrieved_results['ids'][0]:
        return "No relevant context found."
        
    formatted_chunks = []
    
    for i in range(len(retrieved_results['ids'][0])):
        doc_text = retrieved_results['documents'][0][i]
        meta = retrieved_results['metadatas'][0][i]
        
        doc_id = meta.get('document_id', 'Unknown Document')
        heading = meta.get('heading_path', 'Unknown Section')
        
        # Format explicitly for LLM citation parsing
        chunk_str = f"[Source Document: {doc_id} | Section: {heading}]\n{doc_text}\n\n---"
        formatted_chunks.append(chunk_str)
        
    return "\n".join(formatted_chunks)

if __name__ == "__main__":
    # Test the retriever logic
    test_query = "What should I avoid eating if I want to reduce sugar?"
    print("Testing Retrieval Pipeline...\n")
    print(f"Query: '{test_query}'\n")
    
    # Test standard retrieval
    results = retrieve_chunks(test_query, top_k=2)
    formatted = format_context(results)
    
    print("=== FORMATTED CONTEXT FOR LLM ===")
    print(formatted)
    
    # Test filtered retrieval
    print("\n\nTesting Metadata Filtering (Filtering for 'fao-who-healthy-diets')...")
    filtered_results = retrieve_chunks(test_query, top_k=1, document_id="fao-who-healthy-diets")
    filtered_formatted = format_context(filtered_results)
    print("=== FORMATTED FILTERED CONTEXT ===")
    print(filtered_formatted)
