import json
import os
from collections import defaultdict
from data_loader import load_blocks

def format_table(block):
    """Converts a parsed JSON table block into a Markdown-formatted string."""
    headers = block.get("header", [])
    rows = block.get("rows", [])
    
    if not headers and not rows:
        return ""
        
    md_table = []
    
    # Add headers
    if headers:
        md_table.append("| " + " | ".join(headers) + " |")
        md_table.append("|" + "|".join(["---"] * len(headers)) + "|")
        
    # Add rows
    for row in rows:
        md_table.append("| " + " | ".join(row) + " |")
        
    return "\n".join(md_table)

def process_and_chunk_data(input_file: str, output_file: str):
    """
    Groups blocks by document_id and heading_path, formats them appropriately,
    and stores only the required data (text, document_id, heading_path) as chunks.
    """
    blocks = load_blocks(input_file)
    
    # Group by (document_id, tuple(heading_path))
    grouped_chunks = defaultdict(list)
    
    for block in blocks:
        doc_id = block.get("document_id")
        heading_path = tuple(block.get("heading_path", []))
        
        # We exclude blocks that don't have a document_id
        if not doc_id:
            continue
            
        block_type = block.get("type")
        text_content = block.get("text", "")
        
        if block_type == "table":
            text_content = format_table(block)
        elif block_type == "list_item":
            text_content = f"- {text_content}"
            
        if text_content.strip():
            grouped_chunks[(doc_id, heading_path)].append(text_content)
            
    # Assemble into final JSON format
    import uuid
    final_chunks = []
    
    for (doc_id, heading_path), text_list in grouped_chunks.items():
        # Combine texts within the same section
        assembled_text = "\n\n".join(text_list)
        
        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "chunk_text": assembled_text,
            "metadata": {
                "document_id": doc_id,
                "heading_path": list(heading_path)
            }
        }
        final_chunks.append(chunk)
        
    # Ensure data directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
    # Write to output JSON
    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(final_chunks, out_f, indent=2, ensure_ascii=False)
        
    return len(final_chunks)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_filepath = os.path.join(base_dir, 'blocks.jsonl')
    output_filepath = os.path.join(base_dir, 'data', 'processed_chunks.json')
    
    print(f"Processing blocks from {input_filepath}...")
    num_chunks = process_and_chunk_data(input_filepath, output_filepath)
    print(f"Successfully processed data! Stored {num_chunks} semantically grouped chunks into {output_filepath}.")
