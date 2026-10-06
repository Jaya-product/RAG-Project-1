import os
import chromadb
from chromadb.utils import embedding_functions

def view_embeddings():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'chroma_db')
    
    print(f"Connecting to ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    
    collection_name = "dietary_guidance"
    
    # We must provide the same embedding function to access the collection properly
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    collection = client.get_collection(
        name=collection_name,
        embedding_function=embedding_func
    )
    
    print(f"Collection '{collection_name}' currently holds {collection.count()} chunks.\n")
    
    # Get just 2 chunks and explicitly request the embeddings
    results = collection.get(
        limit=2,
        include=['embeddings', 'documents', 'metadatas']
    )
    
    if not results['ids']:
        print("No data found in the collection.")
        return
        
    for i in range(len(results['ids'])):
        chunk_id = results['ids'][i]
        doc = results['documents'][i][:100].replace('\n', ' ')
        meta = results['metadatas'][i]
        embedding = results['embeddings'][i]
        
        print(f"--- Chunk ID: {chunk_id} ---")
        print(f"Document ID: {meta.get('document_id')}")
        print(f"Heading Path: {meta.get('heading_path')}")
        print(f"Text Preview: {doc}...")
        
        # Display the length of the embedding array (should be 384 for bge-small)
        # and print the first 5 floating point numbers as a sample
        print(f"Embedding Dimensions: {len(embedding)}")
        preview_vector = [round(v, 5) for v in embedding[:5]]
        print(f"Embedding Sample (first 5 values): {preview_vector} ...\n")

if __name__ == "__main__":
    view_embeddings()
