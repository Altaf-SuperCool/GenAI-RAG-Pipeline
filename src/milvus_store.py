"""
Milvus Vector Store Implementation
Enterprise-grade distributed vector database using Milvus
"""
import os
from typing import List, Dict, Any, Optional
import numpy as np
from src.vector_store_base import VectorStoreBase

# Import will fail gracefully if pymilvus not installed
try:
    from pymilvus import (
        connections,
        Collection,
        FieldSchema,
        CollectionSchema,
        DataType,
        utility
    )
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False
    print("[MILVUS] Warning: pymilvus not installed. Run: pip install pymilvus")


class MilvusVectorStore(VectorStoreBase):
    """Milvus-based vector store implementation for enterprise-scale similarity search"""
    
    def __init__(
        self,
        collection_name: str = "devops_knowledgebase",
        host: str = "localhost",
        port: int = 19530,
        dimension: int = 384
    ):
        """
        Initialize Milvus vector store
        
        Args:
            collection_name: Name of the Milvus collection
            host: Milvus server host
            port: Milvus server port
            dimension: Embedding vector dimension
        """
        super().__init__(dimension)
        
        if not MILVUS_AVAILABLE:
            raise ImportError(
                "pymilvus is not installed. Install it with: pip install pymilvus"
            )
        
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.collection: Optional[Collection] = None
        self.connected = False
        
        print(f"[MILVUS] Initialized with collection='{collection_name}', "
              f"host={host}:{port}, dimension={dimension}")
    
    def initialize(self) -> None:
        """Initialize Milvus connection and collection"""
        # Connect to Milvus server
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self.connected = True
            print(f"[MILVUS] Connected to server at {self.host}:{self.port}")
            print(f"[MILVUS] Server version: {utility.get_server_version()}")
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Milvus server at {self.host}:{self.port}. "
                f"Make sure Milvus is running. Error: {e}"
            )
        
        # Check if collection exists
        if utility.has_collection(self.collection_name):
            print(f"[MILVUS] Collection '{self.collection_name}' exists, loading...")
            self.collection = Collection(self.collection_name)
            self.collection.load()
            self.total_vectors = self.collection.num_entities
            print(f"[MILVUS] Loaded collection with {self.total_vectors} vectors")
        else:
            print(f"[MILVUS] Creating new collection '{self.collection_name}'...")
            self._create_collection()
    
    def _create_collection(self) -> None:
        """Create a new Milvus collection with schema"""
        # Define schema
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
                description="Primary key"
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.dimension,
                description="Embedding vector"
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=65535,
                description="Document text content"
            ),
            FieldSchema(
                name="source",
                dtype=DataType.VARCHAR,
                max_length=512,
                description="Source document path"
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.INT64,
                description="Page number in source document"
            ),
            FieldSchema(
                name="chunk_index",
                dtype=DataType.INT64,
                description="Chunk index in document"
            )
        ]
        
        schema = CollectionSchema(
            fields,
            description="DevOps Knowledgebase RAG documents"
        )
        
        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema,
            using='default'
        )
        
        # Create index for fast similarity search
        # Using IVF_FLAT for good balance between speed and accuracy
        index_params = {
            "metric_type": "L2",  # L2 distance (same as FAISS IndexFlatL2)
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}  # Number of clusters
        }
        
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        print(f"[MILVUS] Created collection '{self.collection_name}' with IVF_FLAT index")
        self.total_vectors = 0
    
    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """
        Add embeddings to Milvus collection
        
        Args:
            embeddings: NumPy array of shape (n_vectors, dimension)
            metadata: List of metadata dictionaries with keys: text, source, page_number, chunk_index
        """
        if self.collection is None:
            self.initialize()
        
        # Ensure float32
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype('float32')
        
        # Ensure 2D array
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Prepare data
        num_vectors = len(embeddings)
        
        # Extract fields from metadata
        texts = [m.get('text', '')[:65535] for m in metadata]  # Truncate to max length
        sources = [m.get('source', '')[:512] for m in metadata]
        page_numbers = [m.get('page_number', 0) for m in metadata]
        chunk_indices = [m.get('chunk_index', 0) for m in metadata]
        
        # Insert data
        entities = [
            embeddings.tolist(),
            texts,
            sources,
            page_numbers,
            chunk_indices
        ]
        
        insert_result = self.collection.insert(entities)
        
        # Flush to ensure data is persisted
        self.collection.flush()
        
        # Load collection to memory for search
        self.collection.load()
        
        # Update count after flush
        self.total_vectors = self.collection.num_entities
        
        print(f"[MILVUS] Inserted {num_vectors} vectors (total: {self.total_vectors})")
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Milvus
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of results with indices, distances, and metadata
        """
        if self.collection is None or self.total_vectors == 0:
            print("[MILVUS] Warning: Collection is empty")
            return []
        
        # Ensure float32 and proper shape
        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype('float32')
        
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search parameters
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}  # Number of clusters to search
        }
        
        # Perform search
        search_results = self.collection.search(
            data=query_vector.tolist(),
            anns_field="embedding",
            param=search_params,
            limit=min(top_k, self.total_vectors),
            output_fields=["text", "source", "page_number", "chunk_index"]
        )
        
        # Format results
        results = []
        for hits in search_results:
            for hit in hits:
                results.append({
                    'index': hit.id,
                    'distance': float(hit.distance),
                    'metadata': {
                        'text': hit.entity.get('text'),
                        'source': hit.entity.get('source'),
                        'page_number': hit.entity.get('page_number'),
                        'chunk_index': hit.entity.get('chunk_index')
                    }
                })
        
        return results
    
    def save(self) -> None:
        """Flush data to Milvus (data is auto-persisted)"""
        if self.collection is None:
            print("[MILVUS] Warning: No collection to save")
            return
        
        # Milvus auto-persists data, but we can explicitly flush
        self.collection.flush()
        print(f"[MILVUS] Flushed collection '{self.collection_name}' ({self.total_vectors} vectors)")
    
    def load(self) -> None:
        """Load collection into memory for searching"""
        if self.collection is None:
            self.initialize()
        else:
            self.collection.load()
            self.total_vectors = self.collection.num_entities
            print(f"[MILVUS] Loaded collection '{self.collection_name}' ({self.total_vectors} vectors)")
    
    def delete_all(self) -> None:
        """Delete the entire collection"""
        if self.collection is not None:
            collection_name = self.collection_name
            self.collection.release()
            self.collection.drop()
            print(f"[MILVUS] Dropped collection '{collection_name}'")
            self.collection = None
            self.total_vectors = 0
        else:
            print("[MILVUS] No collection to delete")
    
    def disconnect(self) -> None:
        """Disconnect from Milvus server"""
        if self.connected:
            connections.disconnect("default")
            self.connected = False
            print("[MILVUS] Disconnected from server")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Milvus-specific statistics"""
        stats = super().get_stats()
        stats.update({
            'collection_name': self.collection_name,
            'host': self.host,
            'port': self.port,
            'index_type': 'IVF_FLAT',
            'metric': 'L2 (Euclidean)',
            'connected': self.connected
        })
        
        if self.collection is not None:
            stats['is_loaded'] = utility.loading_progress(self.collection_name)
        
        return stats
    
    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()


if __name__ == "__main__":
    # Test Milvus vector store
    print("Testing Milvus Vector Store...")
    print("Note: Requires Milvus server running on localhost:19530")
    print("Start Milvus with: docker-compose up -d")
    print()
    
    try:
        # Create store
        store = MilvusVectorStore(
            collection_name="test_collection",
            dimension=384
        )
        store.initialize()
        
        # Add some test vectors
        test_embeddings = np.random.rand(100, 384).astype('float32')
        test_metadata = [
            {
                'text': f'Test document {i} with some sample text content',
                'source': f'test_doc_{i}.pdf',
                'page_number': i % 10,
                'chunk_index': i
            }
            for i in range(100)
        ]
        store.add_embeddings(test_embeddings, test_metadata)
        
        # Save
        store.save()
        
        # Search
        query = np.random.rand(384).astype('float32')
        results = store.search(query, top_k=5)
        print(f"\nSearch results: {len(results)} found")
        for r in results[:3]:
            print(f"  - ID: {r['index']}, Distance: {r['distance']:.4f}")
            print(f"    Text: {r['metadata']['text'][:50]}...")
            print(f"    Source: {r['metadata']['source']}, Page: {r['metadata']['page_number']}")
        
        # Stats
        print(f"\nStats: {store.get_stats()}")
        
        # Cleanup
        print("\nCleaning up test collection...")
        store.delete_all()
        store.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Milvus is running:")
        print("  docker-compose up -d")
