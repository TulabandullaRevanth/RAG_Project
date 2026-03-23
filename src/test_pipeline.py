import requests
import json

def test_query():
    print("Testing Ingestion...")
    res_ingest = requests.post("http://localhost:8000/ingest-directory")
    print(f"Ingest Response: {res_ingest.status_code} - {res_ingest.text}")
    
    print("\nTesting Query...")
    payload = {
        "query": "What is the HR leave policy?",
        "role": "admin"
    }
    res_query = requests.post("http://localhost:8000/query", json=payload)
    print(f"Query Response: {res_query.status_code}")
    if res_query.status_code == 200:
        print(json.dumps(res_query.json(), indent=2))
    else:
        print(res_query.text)

if __name__ == "__main__":
    try:
        test_query()
    except Exception as e:
        print(f"Connection Error: {e}")
