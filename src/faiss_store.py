"""
FAISS Vector Store Implementation
Fast similarity search using Facebook AI Similarity Search (FAISS)
"""
import os
import pickle
from typing import List, Dict, Any
import numpy as np
import faiss
from src.vector_store_base import VectorStoreBase


class FaissVectorStore(VectorStoreBase):
    """FAISS-based vector store implementation for fast local similarity search"""
    
    def __init__(self, persist_dir: str = "data/vector_store", dimension: int = 384):
        """
        Initialize FAISS vector store
        
        Args:
            persist_dir: Directory to persist index and metadata
            dimension: Embedding vector dimension
        """
        super().__init__(dimension)
        self.persist_dir = persist_dir
        self.index_path = os.path.join(persist_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(persist_dir, "metadata.pkl")
        self.index = None
        self.metadata = []
        
        # Create directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        print(f"[FAISS] Initialized with dimension={dimension}, persist_dir={persist_dir}")
    
    def initialize(self) -> None:
        """Initialize FAISS index"""
        # Try to load existing index
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            print(f"[FAISS] Found existing index, loading...")
            self.load()
        else:
            print(f"[FAISS] Creating new index...")
            # Use IndexFlatL2 for exact L2 (Euclidean) distance search
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            self.total_vectors = 0
            print(f"[FAISS] Created new IndexFlatL2 with dimension={self.dimension}")
    
    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """
        Add embeddings to FAISS index
        
        Args:
            embeddings: NumPy array of shape (n_vectors, dimension)
            metadata: List of metadata dictionaries
        """
        if self.index is None:
            self.initialize()
        
        # Ensure embeddings are float32 (required by FAISS)
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype('float32')
        
        # Ensure 2D array
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store metadata
        self.metadata.extend(metadata)
        
        # Update count
        self.total_vectors = self.index.ntotal
        
        print(f"[FAISS] Added {len(embeddings)} vectors (total: {self.total_vectors})")
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using L2 distance
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of results with indices, distances, and metadata
        """
        if self.index is None or self.total_vectors == 0:
            print("[FAISS] Warning: Index is empty")
            return []
        
        # Ensure float32 and 2D shape
        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype('float32')
        
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_vector, min(top_k, self.total_vectors))
        
        # Format results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append({
                    'index': int(idx),
                    'distance': float(dist),
                    'metadata': self.metadata[idx]
                })
        
        return results
    
    def save(self) -> None:
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            print("[FAISS] Warning: No index to save")
            return
        
        # Save FAISS index
        faiss.write_index(self.index, self.index_path)
        
        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"[FAISS] Saved index ({self.total_vectors} vectors) to {self.persist_dir}")
    
    def load(self) -> None:
        """Load FAISS index and metadata from disk"""
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"Index file not found: {self.index_path}")
        
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        
        # Load FAISS index
        self.index = faiss.read_index(self.index_path)
        
        # Load metadata
        with open(self.metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        
        # Update count
        self.total_vectors = self.index.ntotal
        
        print(f"[FAISS] Loaded {self.total_vectors} vectors from {self.persist_dir}")
    
    def delete_all(self) -> None:
        """Delete all vectors and reset index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self.total_vectors = 0
        
        # Remove files if they exist
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)
        
        print(f"[FAISS] Deleted all vectors and reset index")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get FAISS-specific statistics"""
        stats = super().get_stats()
        stats.update({
            'index_type': 'IndexFlatL2',
            'metric': 'L2 (Euclidean)',
            'persist_dir': self.persist_dir,
            'index_size_mb': os.path.getsize(self.index_path) / (1024 * 1024) if os.path.exists(self.index_path) else 0
        })
        return stats


if __name__ == "__main__":
    # Test FAISS vector store
    print("Testing FAISS Vector Store...")
    
    # Create store
    store = FaissVectorStore(dimension=384)
    store.initialize()
    
    # Add some test vectors
    test_embeddings = np.random.rand(100, 384).astype('float32')
    test_metadata = [{'text': f'Document {i}', 'id': i} for i in range(100)]
    store.add_embeddings(test_embeddings, test_metadata)
    
    # Save
    store.save()
    
    # Search
    query = np.random.rand(384).astype('float32')
    results = store.search(query, top_k=5)
    print(f"\nSearch results: {len(results)} found")
    for r in results[:3]:
        print(f"  - Index: {r['index']}, Distance: {r['distance']:.4f}, Text: {r['metadata']['text']}")
    
    # Stats
    print(f"\nStats: {store.get_stats()}")
