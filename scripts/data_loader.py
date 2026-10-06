import json
import os
from typing import Iterator, Dict, Any

def load_blocks(file_path: str) -> Iterator[Dict[str, Any]]:
    """
    Reads a JSONL file and yields parsed JSON objects (blocks).
    
    Args:
        file_path (str): The path to the blocks.jsonl file.
        
    Yields:
        dict: A parsed JSON object representing a document block.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist. Make sure it is in the project root.")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON on line {line_num}: {e}")

if __name__ == "__main__":
    # Simple test to verify data loading works
    # This points to the blocks.jsonl file located in the root of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'blocks.jsonl')
    
    print(f"Attempting to load data from {file_path}...")
    
    try:
        blocks_generator = load_blocks(file_path)
        first_block = next(blocks_generator)
        print("Successfully loaded blocks! Here is a preview of the first block:")
        print(json.dumps(first_block, indent=2))
        
        # Count total blocks just to verify full loading capability
        total_blocks = 1 + sum(1 for _ in blocks_generator)
        print(f"\nTotal blocks found in dataset: {total_blocks}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except StopIteration:
        print("Error: The file is empty or contains no valid JSON lines.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
