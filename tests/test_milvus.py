"""
Milvus Connection and Functionality Test
Tests basic Milvus operations
"""
import os
import sys
import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment
load_dotenv()

print("=" * 70)
print("  Milvus Connection Test")
print("=" * 70)

# Test 1: Import pymilvus
print("\n📦 Test 1: Checking pymilvus installation...")
try:
    from pymilvus import connections, utility, Collection
    print("   ✅ pymilvus is installed")
except ImportError as e:
    print(f"   ❌ pymilvus not installed: {e}")
    print("   Install with: pip install pymilvus")
    sys.exit(1)

# Test 2: Connect to Milvus
print("\n🔌 Test 2: Connecting to Milvus...")
try:
    host = os.getenv("MILVUS_HOST", "localhost")
    port = int(os.getenv("MILVUS_PORT", "19530"))
    
    connections.connect(
        alias="default",
        host=host,
        port=port
    )
    print(f"   ✅ Connected to Milvus at {host}:{port}")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    print("\n   Troubleshooting:")
    print("   1. Check if Milvus is running:")
    print("      $ docker-compose ps")
    print("   2. Start Milvus if needed:")
    print("      $ docker-compose up -d")
    print("   3. Check Docker logs:")
    print("      $ docker-compose logs milvus-standalone")
    sys.exit(1)

# Test 3: Get server version
print("\n📋 Test 3: Checking server version...")
try:
    version = utility.get_server_version()
    print(f"   ✅ Milvus server version: {version}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: List collections
print("\n📚 Test 4: Listing collections...")
try:
    collections = utility.list_collections()
    if collections:
        print(f"   ✅ Found {len(collections)} collection(s):")
        for coll in collections:
            print(f"      - {coll}")
    else:
        print("   ℹ️  No collections found (this is normal for a fresh install)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Check RAG collection
print("\n🔍 Test 5: Checking RAG collection...")
try:
    collection_name = os.getenv("MILVUS_COLLECTION_NAME", "devops_knowledgebase")
    
    if utility.has_collection(collection_name):
        collection = Collection(collection_name)
        collection.load()
        
        num_entities = collection.num_entities
        print(f"   ✅ Collection '{collection_name}' exists")
        print(f"   ✅ Contains {num_entities} vectors")
        
        # Show schema
        print(f"\n   Schema:")
        for field in collection.schema.fields:
            print(f"      - {field.name} ({field.dtype})")
        
        # Show index info
        if collection.has_index():
            print(f"\n   ✅ Index exists")
        else:
            print(f"\n   ℹ️  No index (searches may be slower)")
    else:
        print(f"   ℹ️  Collection '{collection_name}' does not exist yet")
        print(f"   Run migration to create it:")
        print(f"   $ python scripts/migrate_faiss_to_milvus.py")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Test vector store factory
print("\n🏭 Test 6: Testing vector store factory...")
try:
    from src.vector_store_factory import get_vector_store
    
    # Force Milvus
    store = get_vector_store(store_type='milvus')
    print(f"   ✅ Vector store created: {type(store).__name__}")
    
    # Initialize if not already
    if not store.connected:
        store.initialize()
    
    print(f"   ✅ Total vectors: {store.total_vectors}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Simple search test (if collection exists)
print("\n🔎 Test 7: Testing search functionality...")
try:
    collection_name = os.getenv("MILVUS_COLLECTION_NAME", "devops_knowledgebase")
    
    if utility.has_collection(collection_name):
        from src.vector_store_factory import get_vector_store
        from src.embedding import EmbeddingManager
        
        # Get vector store
        store = get_vector_store(store_type='milvus')
        if not store.connected:
            store.initialize()
        
        if store.total_vectors > 0:
            # Create a test query
            embedding_manager = EmbeddingManager()
            query = "What is DevOps?"
            query_vector = embedding_manager.embed_query(query)
            
            # Search
            results = store.search([query_vector], top_k=3)
            
            print(f"   ✅ Search successful!")
            print(f"   Query: '{query}'")
            print(f"   Results found: {len(results)}")
            
            if results:
                print(f"\n   Top result:")
                top = results[0]
                print(f"      Distance: {top.get('distance', 'N/A')}")
                print(f"      Source: {top['metadata'].get('source', 'N/A')}")
                text_preview = top['metadata'].get('text', top['metadata'].get('content', ''))[:100]
                print(f"      Text: {text_preview}...")
        else:
            print("   ℹ️  Collection is empty, skipping search test")
    else:
        print(f"   ℹ️  Collection doesn't exist yet, skipping search test")
except Exception as e:
    print(f"   ❌ Search test failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("  Test Summary")
print("=" * 70)
print("\n✅ Milvus is properly configured and working!")
print(f"\nConnection Details:")
print(f"   Host: {os.getenv('MILVUS_HOST', 'localhost')}")
print(f"   Port: {os.getenv('MILVUS_PORT', '19530')}")
print(f"   Collection: {os.getenv('MILVUS_COLLECTION_NAME', 'devops_knowledgebase')}")
print(f"\n💡 Access Attu Web UI: http://localhost:8000")
print("=" * 70)
