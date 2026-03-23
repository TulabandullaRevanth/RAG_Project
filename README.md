# RBAC-RAG system

This project is a professional **RBAC-RAG system** designed for on-premises deployment. It features a robust multi-layered security architecture ensuring that users only access information permitted by their organizational role.

## Quick Start Instructions

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) (Local LLM server)
  - Required model: `mistral` (7B). Run `ollama pull mistral` before starting.

### Setup & Run
1. **Unzip/Clone** the project folder.
2. **Install Dependencies**:
   ```bash
   cd src
   pip install -r requirements.txt
   ```
3. **Start the Backend (FastAPI)**:
   ```bash
   python app.py
   ```
   *The backend will run on http://localhost:8000*
4. **Start the Frontend (Streamlit)**:
   ```bash
   streamlit run ui.py
   ```
   *The UI will open in your browser.*

### Initializing the System
1. Open the Streamlit UI.
2. Click **" Ingest Document Directory"** in the sidebar. This will prepopulate the vector index with the files in the `data/` folder.
3. Use the **User Configuration** dropdown to test different roles.

---

##  Technology Stack & Rationale

- **Backend**: **FastAPI**. High performance, easy to prototype, and supports asynchronous operations which is crucial for LLM calls.
- **Frontend**: **Streamlit**. Ideal for data-heavy applications and internal tools, allowing for rapid UI development without deep JS knowledge.
- **Vector Store**: **FAISS** (Local). A highly efficient library for similarity search that doesn't require a separate database server, fitting the on-premises requirement.
- **Embeddings**: **Sentence-Transformers** (`all-MiniLM-L6-v2`). Runs locally on CPU/GPU, providing high-quality semantic representations without external APIs.
- **LLM**: **Ollama** (Local). The standard for self-hosted LLMs, featuring the high-performance **Mistral (7B)** model for Reasoning and RBAC compliance.

---

##  RBAC Implementation & Design

The system implements **Defense in Depth** with two primary layers of enforcement:

1. **Retrieval-Layer Filter (Hard Enforcement)**: Before the LLM even sees the context, the system metadata-filters retrieved chunks. If a user's role doesn't have permits for a specific department (e.g., `employee` vs `Finance`), those chunks are physically removed from the context.
2. **Prompt-Layer Instructions (Soft Enforcement)**: The system prompt explicitly instructs the LLM to cross-reference the user's role against the provided context metadata. This handles edge cases like "Summary-only" access where retrieval is allowed but disclosure of fine-grained detail is forbidden.

### Role Table
| Role | Finance | Legal | HR |
|------|---------|-------|----|
| admin | Full | Full | Full |
| manager | Full | Summary Only | Full |
| employee | None | None | Own Records Only |
| auditor | Full | Full | None |

---

##  Tradeoffs & Future Decisions

### Current Tradeoffs
- **In-Memory Metadata**: Metadata is currently handled via `pickle`. For production with millions of documents, a DB like PostgreSQL with `pgvector` or Qdrant would be preferred for persistence and complex querying.
- **Synchronous LLM**: While the backend is FastAPI, the request to Ollama is blocking. Moving to a message queue (RabbitMQ/Celery) would improve reliability for high-concurrency scenarios.

### What I'd Do Differently with More Time
- Implement **Advanced Chunking**: Recursive character splitting with overlap to preserve semantic context across chunk boundaries.
- **Hybrid Search**: Combine semantic search (FAISS) with keyword search (BM25) for better retrieval on specific terms (e.g., policy IDs).
- **User Authentication**: Replace the simple UI select-box with a real OAuth2/JWT system for secure role propagation.
