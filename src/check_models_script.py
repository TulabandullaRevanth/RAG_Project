
import os
import requests
from sentence_transformers import SentenceTransformer

def check_embedding():
    print("Checking Embedding Model (all-MiniLM-L6-v2)...")
    try:
        # Load local model (should be cached)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        emb = model.encode(["Hello world"])
        print(f"Embedding success. Shape: {emb.shape}")
        return True
    except Exception as e:
        print(f"Embedding error: {e}")
        return False

def check_ollama_llm():
    print("\nChecking Ollama LLM (mistral)...")
    try:
        import ollama
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": "Say 'Model Check OK' if you can hear me."}]
        )
        res_text = response["message"]["content"]
        print(f"Ollama response: {res_text}")
        return True
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return False

if __name__ == "__main__":
    e_ok = check_embedding()
    o_ok = check_ollama_llm()
    
    if e_ok and o_ok:
        print("\nSUMMARY: Both models are working correctly.")
    else:
        print("\nSUMMARY: System has issues with models.")
