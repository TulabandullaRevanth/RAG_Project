import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2', index_path='faiss_index.bin', metadata_path='metadata.pkl'):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def add_documents(self, documents):
        """
        documents: list of dict {'content': str, 'metadata': {'department': str, 'filename': str}}
        """
        if not documents:
            return
            
        texts = [doc['content'] for doc in documents]
        embeddings = self.model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
        
        for doc in documents:
            self.metadata.append(doc['metadata'])
            
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def search(self, query, k=5):
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append({
                    'content': self._get_content_by_index(idx), 
                    'metadata': self.metadata[idx],
                    'score': float(distances[0][i])
                })
        return results

    def _get_content_by_index(self, idx):
        # In a real system, we'd store content in a DB or as part of metadata.
        # For simplicity, we'll store content in metadata if small or re-read from file.
        # Here, let's assume we store the content directly in metadata during ingestion.
        return self.metadata[idx].get('content', '')

    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)
