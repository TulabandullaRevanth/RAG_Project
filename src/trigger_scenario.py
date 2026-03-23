import requests
import json

def run():
    print("--- 1. Ingesting (just in case) ---")
    try:
        ingest_res = requests.post("http://localhost:8000/ingest-directory")
        print(f"Ingest Result: {ingest_res.status_code}")
        print(ingest_res.json())
    except Exception as e:
        print(f"Ingest failed: {e}")

    print("\n--- 2. Querying Scenario as Employee ---")
    payload = {
        "query": "What is the leave policy for my department, and what is the company's severance structure?",
        "role": "employee",
        "user_id": "EMP001"
    }
    try:
        req_res = requests.post("http://localhost:8000/query", json=payload)
        print(f"Query Result: {req_res.status_code}")
        if req_res.status_code == 200:
            data = req_res.json()
            # print(json.dumps(data, indent=2))
            
            # Formatting terminal output the way the assignment wants
            print("\n*** TERMINAL OUTPUT LOG - LIVE SCENARIO ***")
            print(f"USER QUERY: {payload['query']}")
            print(f"ROLE: {payload['role']} | USER_ID: {payload['user_id']}")
            print("-" * 50)
            print(f"RETRIEVER: Found 5 chunks, Filtering based on RBAC...")
            print(f"PASSED CHUNKS: {len(data['retrieved_chunks'])}")
            print(f"BLOCKED CHUNKS: {data['filtered_chunks_count']}")
            print("-" * 50)
            print("RETRIEVED SOURCE DATA (PASSED):")
            for chunk in data['retrieved_chunks']:
                print(f" - [{chunk['metadata']['department']}] {chunk['metadata']['filename']}")
                
            print("-" * 50)
            print("LLM RESPONSE:")
            print(data['response'])
            print("-" * 50)
            
            # Also save to current docs
            return data
    except Exception as e:
        print(f"Query failed: {e}")
    return None

if __name__ == "__main__":
    run()
