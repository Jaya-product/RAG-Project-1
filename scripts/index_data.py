import json
import os
import chromadb
from chromadb.utils import embedding_functions

def index_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'data', 'processed_chunks.json')
    db_path = os.path.join(base_dir, 'chroma_db')
    
    # 1. Load the processed chunks
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Cannot find {input_file}")
        
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    print(f"Loaded {len(chunks)} chunks from {input_file}")

    # 2. Initialize ChromaDB client (Persistent)
    client = chromadb.PersistentClient(path=db_path)
    
    # 3. Initialize Embedding Model (BAAI/bge-small-en-v1.5)
    print("Initializing embedding model (BAAI/bge-small-en-v1.5)...")
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    collection_name = "dietary_guidance"
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name, 
        embedding_function=embedding_func
    )
    
    ids = []
    documents = []
    metadatas = []
    
    # 4. Prepare data for indexing
    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["chunk_text"])
        
        # Serialize heading_path list to a string for ChromaDB metadata compatibility
        meta = chunk.get("metadata", {})
        heading_path_str = " > ".join(meta.get("heading_path", []))
        
        metadatas.append({
            "document_id": meta.get("document_id", ""),
            "heading_path": heading_path_str
        })
        
    # 5. Upsert to Vector Database
    print(f"Generating embeddings and upserting {len(ids)} chunks into ChromaDB...")
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Successfully indexed chunks into ChromaDB at {db_path}!")

    # 6. Simple Validation Query
    test_query = "How long can I freeze meat?"
    print(f"\n--- Validation Test ---")
    print(f"Query: '{test_query}'")
    
    results = collection.query(
        query_texts=[test_query],
        n_results=2
    )
    
    if results and results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            print(f"\nResult {i+1}:")
            print(f"Document ID: {results['metadatas'][0][i]['document_id']}")
            print(f"Heading Path: {results['metadatas'][0][i]['heading_path']}")
            preview = results['documents'][0][i][:100].replace('\n', ' ')
            print(f"Preview: {preview}...")
    else:
        print("No results returned for the validation query.")

if __name__ == "__main__":
    index_data()
