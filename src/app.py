import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import glob
import re
from vector_store import VectorStore
from rbac import RBACSystem
from model_client import OllamaClient, PromptManager

app = FastAPI()

# Initialize global components
vs = VectorStore()
rbac = RBACSystem()
model_client = OllamaClient()
prompt_manager = PromptManager()

class QueryRequest(BaseModel):
    query: str
    role: str
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    retrieved_chunks: List[dict]
    filtered_chunks_count: int
    full_prompt: str

def chunk_text(text, size=500, overlap=50):
    # Simple chunking by characters, could be improved by sentence split
    chunks = []
    if len(text) <= size:
        return [text]
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i : i + size])
    return chunks

@app.on_event("startup")
async def startup_event():
    if not os.path.exists("data"):
        os.makedirs("data")

@app.post("/ingest-directory")
async def ingest_directory(path: Optional[str] = None):
    """
    Ingests all documents, looking for 'data' in common locations relative to src.
    """
    if path is None:
        # Try finding 'data' in current or parent directory
        if os.path.exists("data"):
            path = "data"
        elif os.path.exists("../data"):
            path = "../data"
        else:
            # Fallback/Auto-create
            path = "data"
            os.makedirs(path, exist_ok=True)
            
    files = glob.glob(os.path.join(path, "*.txt"))
    added_docs = []
    
    for f in files:
        filename = os.path.basename(f)
        content = ""
        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            
        # Determine department based on filename (e.g., finance_q4_budget.txt -> Finance)
        dept = 'General'
        if 'finance' in filename.lower(): dept = 'Finance'
        elif 'hr' in filename.lower(): dept = 'HR'
        elif 'legal' in filename.lower(): dept = 'Legal'
        
        # Determine owner for HR docs (simulate)
        user_owner = 'ALL' # Default for HR docs (public to HR)
        if dept == 'HR':
            if 'private' in filename.lower() or 'record' in filename.lower():
                user_owner = 'EMP001' # Simulated private record
            else:
                user_owner = 'ALL' # Shared HR docs (policies, handbook)
            
        # Chunking before ingestion
        text_chunks = chunk_text(content)
        for chunk in text_chunks:
            added_docs.append({
                'content': chunk,
                'metadata': {
                    'department': dept,
                    'filename': filename,
                    'user_id': user_owner,
                    'content': chunk  # Store content directly in metadata
                }
            })
        
    vs.add_documents(added_docs)
    return {"status": "success", "count": len(files), "chunks": len(added_docs)}

@app.post("/query", response_model=QueryResponse)
async def process_query(req: QueryRequest):
    # Log info for debugging
    print(f"--- Processing Query Role={req.role} ---")
    print(f"Total chunks in vector store: {len(vs.metadata)}")
    
    # Retrieve top K (K=3 for faster processing)
    raw_results = vs.search(req.query, k=3)
    print(f"Found {len(raw_results)} chunks from semantic search.")
    
    # Apply RBAC filtering
    results_after_rbac = rbac.filter_documents(raw_results, req.role, req.user_id)
    
    # Deduplicate results by content to avoid UI clutter and LLM confusion
    filtered_results = []
    seen_content = set()
    for res in results_after_rbac:
        content_hash = res.get('content', '').strip()
        if content_hash not in seen_content:
            filtered_results.append(res)
            seen_content.add(content_hash)
    
    # Generate Prompt and Deduplicate context for UI visibility/consistency
    system_prompt = prompt_manager.get_system_prompt(req.role, req.user_id)
    
    unique_contents = []
    for chunk in filtered_results:
        content = chunk.get('content', '').strip()
        if content not in unique_contents:
            unique_contents.append(content)
            
    combined_context = "\n\n".join(unique_contents)
    full_prompt = f"System: {system_prompt}\n\nContext: {combined_context}\n\nUser: {req.query}"
    
    # Generation
    response = model_client.generate_response(system_prompt, req.query, filtered_results)
    
    return QueryResponse(
        response=response,
        retrieved_chunks=filtered_results,
        filtered_chunks_count=len(raw_results) - len(filtered_results),
        full_prompt=full_prompt
    )

@app.post("/clear")
async def clear_index():
    vs.clear()
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
