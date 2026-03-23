import streamlit as st
import requests
import json
import base64

# Simple UI for RBAC RAG System
st.set_page_config(page_title="RBAC-RAG system", layout="wide")

st.title(" RBAC-RAG system")
st.markdown("---")

# Sidebar for User role and Settings
with st.sidebar:
    st.header("User Configuration")
    role = st.selectbox("Current Role", ["admin", "manager", "employee", "auditor"])
    user_id = st.text_input("User ID (for HR records)", value="EMP001")
    
    st.header("Core Controls")
    uploaded_files = st.file_uploader(
        "Upload sensitive documents (.txt)", 
        type=["txt"], 
        accept_multiple_files=True
    )
    if uploaded_files:
        if st.button(f"💾 Save {len(uploaded_files)} file(s) to Data Store"):
            import os
            saved = []
            for uploaded_file in uploaded_files:
                save_path = os.path.join("data", uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved.append(uploaded_file.name)
            st.success(f"Saved {len(saved)} file(s): {', '.join(saved)}. Click Ingest to update index.")

    if st.button(" Ingest Document Directory"):
        with st.spinner("Processing documents..."):
            try:
                # Assuming backend runs on 8000
                res = requests.post("http://localhost:8000/ingest-directory")
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Ingested {data['count']} files into {data['chunks']} chunks!")
                else:
                    st.error("Ingestion failed. Check backend.")
            except Exception as e:
                st.error(f"Error: {e}")
                
    if st.button(" Clear Vector Index"):
        try:
            res = requests.post("http://localhost:8000/clear")
            if res.status_code == 200:
                st.info("Index cleared successfully.")
        except Exception as e:
            st.error(f"Error: {e}")

# Main Chat Interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Query System")
    query = st.text_area("Enter your query:", placeholder="e.g., What is the HR leave policy?")
    
    if st.button("Ask System"):
        if not query:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Retrieving and Generating..."):
                try:
                    payload = {
                        "query": query,
                        "role": role,
                        "user_id": user_id
                    }
                    res = requests.post("http://localhost:8000/query", json=payload)
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.subheader(" AI Response")
                        st.write(data['response'])
                        
                        with st.expander("Show Full Prompt (Debug)"):
                            st.text(data['full_prompt'])

                        # Extra context for visualization
                        with col2:
                            st.header("Retrieval Stats")
                            st.metric("Retrieved Chunks", len(data['retrieved_chunks']))
                            st.metric("Blocked Chunks", data['filtered_chunks_count'])
                            
                            st.subheader("Passed Context Chunks")
                            for idx, chunk in enumerate(data['retrieved_chunks']):
                                with st.expander(f"Chunk {idx+1}: {chunk['metadata']['filename']}"):
                                    st.write(f"**Dept:** {chunk['metadata']['department']}")
                                    st.write(f"**Content Snippet:** {chunk['content'][:200]}...")
                                    st.write(f"**Score:** {chunk['score']:.4f}")
                    else:
                        st.error(f"Query failed: {res.text}")
                except Exception as e:
                    st.error(f"Could not connect to Backend: {e}")

# Display current configuration summary for reference
st.info(f"Currently acting as **{role.upper()}** (User ID: {user_id})")
