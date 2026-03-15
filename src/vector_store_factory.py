"""
Vector Store Factory
Creates the appropriate vector store implementation based on configuration
"""
import os
from typing import Optional
from dotenv import load_dotenv
from src.vector_store_base import VectorStoreBase
from src.faiss_store import FaissVectorStore
from src.milvus_store import MilvusVectorStore

# Load environment variables
load_dotenv()


def get_vector_store(
    store_type: Optional[str] = None,
    dimension: int = 384,
    **kwargs
) -> VectorStoreBase:
    """
    Factory function to create vector store instance based on configuration
    
    Args:
        store_type: Type of vector store ('faiss' or 'milvus'). 
                   If None, reads from VECTOR_DB_TYPE env variable
        dimension: Embedding vector dimension
        **kwargs: Additional configuration passed to the specific implementation
        
    Returns:
        VectorStoreBase: Initialized vector store instance
        
    Environment Variables:
        VECTOR_DB_TYPE: 'faiss' or 'milvus' (default: 'faiss')
        MILVUS_HOST: Milvus server host (default: 'localhost')
        MILVUS_PORT: Milvus server port (default: 19530)
        MILVUS_COLLECTION_NAME: Collection name (default: 'devops_knowledgebase')
        
    Examples:
        >>> # Use default from .env
        >>> store = get_vector_store(dimension=384)
        
        >>> # Force FAISS
        >>> store = get_vector_store(store_type='faiss', persist_dir='my_data')
        
        >>> # Force Milvus
        >>> store = get_vector_store(store_type='milvus', collection_name='my_docs')
    """
    # Determine store type
    if store_type is None:
        store_type = os.getenv('VECTOR_DB_TYPE', 'faiss').lower()
    else:
        store_type = store_type.lower()
    
    # Validate store type
    if store_type not in ['faiss', 'milvus']:
        raise ValueError(
            f"Invalid vector store type: '{store_type}'. "
            f"Must be 'faiss' or 'milvus'"
        )
    
    # Create appropriate store
    if store_type == 'faiss':
        print(f"[FACTORY] Creating FAISS vector store...")
        
        # Get FAISS-specific config
        persist_dir = kwargs.get('persist_dir', 'data/vector_store')
        
        store = FaissVectorStore(
            persist_dir=persist_dir,
            dimension=dimension
        )
        
    elif store_type == 'milvus':
        print(f"[FACTORY] Creating Milvus vector store...")
        
        # Get Milvus-specific config from env or kwargs
        host = kwargs.get('host', os.getenv('MILVUS_HOST', 'localhost'))
        port = kwargs.get('port', int(os.getenv('MILVUS_PORT', '19530')))
        collection_name = kwargs.get(
            'collection_name',
            os.getenv('MILVUS_COLLECTION_NAME', 'devops_knowledgebase')
        )
        
        store = MilvusVectorStore(
            collection_name=collection_name,
            host=host,
            port=port,
            dimension=dimension
        )
    
    # Initialize the store
    store.initialize()
    
    print(f"[FACTORY] Successfully created {store.__class__.__name__}")
    return store


def get_vector_store_info() -> dict:
    """
    Get information about configured vector store without initializing it
    
    Returns:
        Dictionary with vector store configuration info
    """
    store_type = os.getenv('VECTOR_DB_TYPE', 'faiss').lower()
    
    info = {
        'type': store_type,
        'available_types': ['faiss', 'milvus']
    }
    
    if store_type == 'faiss':
        info['config'] = {
            'persist_dir': 'data/vector_store',
            'index_type': 'IndexFlatL2',
            'metric': 'L2 (Euclidean)'
        }
    elif store_type == 'milvus':
        info['config'] = {
            'host': os.getenv('MILVUS_HOST', 'localhost'),
            'port': os.getenv('MILVUS_PORT', '19530'),
            'collection_name': os.getenv('MILVUS_COLLECTION_NAME', 'devops_knowledgebase'),
            'index_type': 'IVF_FLAT',
            'metric': 'L2 (Euclidean)'
        }
    
    return info


if __name__ == "__main__":
    # Test factory
    print("Testing Vector Store Factory\n")
    print("=" * 60)
    
    # Show configuration
    print("Current Configuration:")
    info = get_vector_store_info()
    print(f"  Type: {info['type']}")
    print(f"  Config: {info['config']}")
    print()
    
    # Test FAISS creation
    print("=" * 60)
    print("Test 1: Create FAISS store")
    print("=" * 60)
    try:
        store = get_vector_store(store_type='faiss', dimension=384)
        stats = store.get_stats()
        print(f"Stats: {stats}")
        print("✅ FAISS store created successfully\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Test Milvus creation (may fail if server not running)
    print("=" * 60)
    print("Test 2: Create Milvus store")
    print("=" * 60)
    try:
        store = get_vector_store(store_type='milvus', dimension=384)
        stats = store.get_stats()
        print(f"Stats: {stats}")
        print("✅ Milvus store created successfully\n")
        
        # Cleanup test collection
        store.delete_all()
        store.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: Milvus requires server running on localhost:19530")
        print("Start with: docker-compose up -d\n")
    
    # Test using env variable
    print("=" * 60)
    print("Test 3: Create store from environment variable")
    print("=" * 60)
    try:
        store = get_vector_store(dimension=384)
        print(f"Created: {store.__class__.__name__}")
        print(f"Stats: {store.get_stats()}")
        print("✅ Environment-based store created successfully\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
