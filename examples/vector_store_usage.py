"""
Example: Using Vector Store Factory Pattern
Demonstrates how to use flexible vector database backend
"""

from src.vector_store_factory import get_vector_store, get_vector_store_info
import numpy as np

print("=" * 70)
print("Vector Store Factory Pattern - Usage Examples")
print("=" * 70)

# ============================================================================
# Example 1: Check Current Configuration
# ============================================================================
print("\n📋 Example 1: Check Configuration")
print("-" * 70)

info = get_vector_store_info()
print(f"Configured Type: {info['type']}")
print(f"Available Types: {info['available_types']}")
print(f"Configuration: {info['config']}")

# ============================================================================
# Example 2: Create Store Using Default Configuration (from .env)
# ============================================================================
print("\n📦 Example 2: Create Store (Auto from .env)")
print("-" * 70)

# This reads VECTOR_DB_TYPE from .env file
store = get_vector_store(dimension=384)
print(f"✅ Created: {store.__class__.__name__}")
print(f"Stats: {store.get_stats()}")

# ============================================================================
# Example 3: Force Specific Database Type
# ============================================================================
print("\n🔧 Example 3: Force Specific Type")
print("-" * 70)

# Always use FAISS (ignores .env)
faiss_store = get_vector_store(store_type='faiss', dimension=384)
print(f"✅ FAISS Store: {faiss_store.__class__.__name__}")

# Try Milvus (may fail if server not running)
try:
    milvus_store = get_vector_store(store_type='milvus', dimension=384)
    print(f"✅ Milvus Store: {milvus_store.__class__.__name__}")
    milvus_store.disconnect()  # Clean up connection
except Exception as e:
    print(f"⚠️ Milvus not available: {e}")
    print("   (This is expected if Milvus server is not running)")

# ============================================================================
# Example 4: Complete Workflow with FAISS
# ============================================================================
print("\n🔄 Example 4: Complete Workflow (FAISS)")
print("-" * 70)

# Create store
store = get_vector_store(store_type='faiss', dimension=384)

# Generate sample data
print("Generating test data...")
num_docs = 100
embeddings = np.random.rand(num_docs, 384).astype('float32')
metadata = [
    {
        'text': f'This is test document number {i} with sample content about AI and machine learning.',
        'source': f'test_doc_{i % 10}.pdf',
        'page_number': i % 20,
        'chunk_index': i
    }
    for i in range(num_docs)
]

# Add embeddings
print(f"Adding {num_docs} documents...")
store.add_embeddings(embeddings, metadata)
print(f"✅ Added successfully. Total vectors: {store.total_vectors}")

# Save
print("Saving to disk...")
store.save()
print("✅ Saved")

# Search
print("Performing search...")
query_vector = np.random.rand(384).astype('float32')
results = store.search(query_vector, top_k=5)

print(f"✅ Found {len(results)} results:")
for i, result in enumerate(results[:3], 1):
    print(f"  {i}. Distance: {result['distance']:.4f}")
    print(f"     Source: {result['metadata']['source']}")
    print(f"     Text: {result['metadata']['text'][:60]}...")

# Stats
stats = store.get_stats()
print(f"\n📊 Final Stats:")
print(f"   Type: {stats['type']}")
print(f"   Total Vectors: {stats['total_vectors']}")
print(f"   Dimension: {stats['dimension']}")
if 'index_size_mb' in stats:
    print(f"   Index Size: {stats['index_size_mb']:.2f} MB")

# ============================================================================
# Example 5: Switching Databases (Demonstration)
# ============================================================================
print("\n🔄 Example 5: Database Switching Demo")
print("-" * 70)

print("""
To switch from FAISS to Milvus:

1. Update .env file:
   VECTOR_DB_TYPE=milvus
   
2. Start Milvus server:
   docker-compose up -d
   
3. Install pymilvus:
   pip install pymilvus
   
4. Your code stays the same!
   store = get_vector_store(dimension=384)
   
The factory automatically uses the configured backend!
""")

# ============================================================================
# Example 6: Custom Configuration
# ============================================================================
print("\n⚙️ Example 6: Custom Configuration")
print("-" * 70)

# FAISS with custom directory
custom_faiss = get_vector_store(
    store_type='faiss',
    dimension=384,
    persist_dir='custom_vector_data'
)
print(f"✅ Custom FAISS: {custom_faiss.persist_dir}")

# Milvus with custom settings (won't connect without server)
print("""
Milvus with custom settings:

store = get_vector_store(
    store_type='milvus',
    dimension=384,
    host='milvus.mycompany.com',
    port=19530,
    collection_name='my_custom_collection'
)
""")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("✅ Examples Complete!")
print("=" * 70)
print("""
Key Takeaways:
1. Use get_vector_store() - it reads config from .env
2. Override with store_type='faiss' or 'milvus' if needed
3. Same interface works with both backends
4. Switch databases by changing .env - no code changes!

Next Steps:
- Try changing VECTOR_DB_TYPE in .env
- Run this script again to see different backend
- Check VECTOR_DB_GUIDE.md for detailed setup
""")
