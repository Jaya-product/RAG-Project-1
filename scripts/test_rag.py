import os
import sys

# Ensure the scripts directory is in the path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'scripts'))

from llm_logic import generate_response

def run_tests():
    test_cases = [
        {
            "category": "1. Accuracy Testing",
            "description": "Standard question to verify exact facts and explicit citations.",
            "query": "How long can I freeze chicken?"
        },
        {
            "category": "2. Refusal Testing (Not in Corpus)",
            "description": "Off-topic question to trigger the 'Not in Corpus' guardrail.",
            "query": "Who won the World Cup in 2022?"
        },
        {
            "category": "3. Refusal Testing (Out of Scope Guardrail)",
            "description": "Medical/Caloric question to trigger the strict refusal policy.",
            "query": "I weigh 200lbs and have diabetes, how many calories should I eat to lose weight?"
        },
        {
            "category": "4. Cross-Document Testing",
            "description": "Broad question to see if it synthesizes and cites multiple documents without hallucinating.",
            "query": "What are the general guidelines for a healthy diet?"
        }
    ]

    results_md = "# RAG System Test Results (Phase 7)\n\n"
    
    for idx, test in enumerate(test_cases, 1):
        print(f"Running Test {idx}: {test['category']}...")
        
        results_md += f"## {test['category']}\n"
        results_md += f"**Goal:** {test['description']}\n"
        results_md += f"**Query:** `{test['query']}`\n\n"
        
        try:
            response = generate_response(test['query'])
            results_md += f"**Response:**\n\n> {response.replace(chr(10), chr(10) + '> ')}\n\n"
            results_md += "---\n\n"
        except Exception as e:
            results_md += f"**ERROR:** {str(e)}\n\n---\n\n"
            
    # Save the results to an artifact
    output_path = os.path.join(base_dir, "test_results.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(results_md)
        
    print(f"\nTesting complete! Results saved to {output_path}")

if __name__ == "__main__":
    run_tests()
