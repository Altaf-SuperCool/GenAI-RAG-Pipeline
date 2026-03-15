"""
FAISS to Milvus Migration Script
Migrates vector data from FAISS to Milvus vector database
"""
import os
import sys
import numpy as np
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.faiss_store import FaissVectorStore
from src.milvus_store import MilvusVectorStore

# Load environment
load_dotenv()


def migrate_faiss_to_milvus():
    """Migrate vectors and metadata from FAISS to Milvus"""
    
    print("=" * 70)
    print("  FAISS to Milvus Migration")
    print("=" * 70)
    
    # Step 1: Load FAISS data
    print("\n📦 Step 1: Loading data from FAISS...")
    try:
        faiss_store = FaissVectorStore(persist_dir="data/vector_store")
        faiss_store.load()
        print(f"   ✅ Loaded {faiss_store.total_vectors} vectors from FAISS")
    except Exception as e:
        print(f"   ❌ Error loading FAISS: {e}")
        print("   Make sure FAISS index exists at: data/vector_store/")
        return False
    
    if faiss_store.total_vectors == 0:
        print("   ⚠️  No vectors found in FAISS. Nothing to migrate.")
        return False
    
    # Step 2: Initialize Milvus
    print("\n🔌 Step 2: Connecting to Milvus...")
    try:
        milvus_host = os.getenv("MILVUS_HOST", "localhost")
        milvus_port = int(os.getenv("MILVUS_PORT", "19530"))
        collection_name = os.getenv("MILVUS_COLLECTION_NAME", "devops_knowledgebase")
        
        milvus_store = MilvusVectorStore(
            collection_name=collection_name,
            host=milvus_host,
            port=milvus_port,
            dimension=faiss_store.dimension
        )
        milvus_store.initialize()
        print(f"   ✅ Connected to Milvus at {milvus_host}:{milvus_port}")
        
        # Check if collection already has data
        if milvus_store.total_vectors > 0:
            print(f"\n   ⚠️  Warning: Collection '{collection_name}' already contains {milvus_store.total_vectors} vectors")
            response = input("   Do you want to continue and add more vectors? (y/N): ")
            if response.lower() != 'y':
                print("   Migration cancelled.")
                return False
    except ConnectionError as e:
        print(f"   ❌ Error connecting to Milvus: {e}")
        print("\n   Make sure Milvus is running:")
        print("   $ docker-compose up -d")
        return False
    except Exception as e:
        print(f"   ❌ Error initializing Milvus: {e}")
        return False
    
    # Step 3: Extract vectors and metadata from FAISS
    print(f"\n📋 Step 3: Extracting {faiss_store.total_vectors} vectors and metadata...")
    try:
        # FAISS stores vectors in the index
        all_vectors = []
        all_metadata = []
        
        # Retrieve all vectors from FAISS
        # Note: This loads all vectors into memory. For very large datasets,
        # consider batch processing
        for i in range(faiss_store.total_vectors):
            # Get vector from FAISS
            vector = faiss_store.index.reconstruct(int(i))
            all_vectors.append(vector)
            
            # Get metadata
            if i < len(faiss_store.metadata):
                all_metadata.append(faiss_store.metadata[i])
            else:
                # Default metadata if missing
                all_metadata.append({
                    'text': f'Document {i}',
                    'source': 'unknown',
                    'chunk_id': i
                })
        
        print(f"   ✅ Extracted {len(all_vectors)} vectors")
        print(f"   ✅ Extracted {len(all_metadata)} metadata entries")
        
    except Exception as e:
        print(f"   ❌ Error extracting data: {e}")
        return False
    
    # Step 4: Batch insert into Milvus
    print("\n⬆️  Step 4: Inserting data into Milvus...")
    try:
        batch_size = 1000  # Insert in batches of 1000
        total_batches = (len(all_vectors) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, len(all_vectors))
            
            batch_vectors = all_vectors[start_idx:end_idx]
            batch_metadata = all_metadata[start_idx:end_idx]
            
            # Convert list to numpy array for Milvus
            batch_vectors_array = np.array(batch_vectors, dtype=np.float32)
            
            # Ensure metadata has required fields
            processed_metadata = []
            for meta in batch_metadata:
                processed_metadata.append({
                    'text': meta.get('text', meta.get('content', '')),
                    'source': meta.get('source', 'unknown'),
                    'page_number': meta.get('page_number', meta.get('page', 0)),
                    'chunk_index': meta.get('chunk_index', meta.get('chunk_id', 0))
                })
            
            milvus_store.add_embeddings(batch_vectors_array, processed_metadata)
            
            print(f"   Progress: Batch {batch_num + 1}/{total_batches} "
                  f"({end_idx}/{len(all_vectors)} vectors)")
        
        print(f"   ✅ Successfully inserted {len(all_vectors)} vectors")
        
    except Exception as e:
        print(f"   ❌ Error inserting data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Create index for performance
    print("\n🔍 Step 5: Creating search index...")
    try:
        from pymilvus import Collection
        
        collection = Collection(collection_name)
        
        # Check if index already exists
        if collection.has_index():
            print("   ℹ️  Index already exists, skipping creation")
        else:
            # Create IVF_FLAT index for good balance of speed and accuracy
            nlist = min(128, int(np.sqrt(faiss_store.total_vectors)))
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": nlist}
            }
            
            print(f"   Creating IVF_FLAT index with nlist={nlist}...")
            collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            print("   ✅ Index created successfully")
        
        # Load collection into memory
        collection.load()
        print("   ✅ Collection loaded into memory")
        
    except Exception as e:
        print(f"   ⚠️  Warning: Could not create index: {e}")
        print("   The collection is still usable, but searches may be slower")
    
    # Step 6: Verify migration
    print("\n✓  Step 6: Verifying migration...")
    try:
        from pymilvus import Collection
        
        collection = Collection(collection_name)
        final_count = collection.num_entities
        
        print(f"   FAISS vectors: {faiss_store.total_vectors}")
        print(f"   Milvus vectors: {final_count}")
        
        if final_count >= faiss_store.total_vectors:
            print("   ✅ Migration verified successfully!")
        else:
            print(f"   ⚠️  Warning: Vector count mismatch")
    except Exception as e:
        print(f"   ⚠️  Could not verify: {e}")
    
    # Step 7: Test search
    print("\n🧪 Step 7: Testing search functionality...")
    try:
        # Use first vector as query
        test_vector = all_vectors[0]
        results = milvus_store.search([test_vector], top_k=3)
        
        print(f"   ✅ Search test successful: Found {len(results)} results")
        if results:
            print(f"   Top result distance: {results[0].get('distance', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️  Search test failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("  Migration Complete!")
    print("=" * 70)
    print(f"\n✅ Successfully migrated {len(all_vectors)} vectors from FAISS to Milvus")
    print(f"✅ Collection: {collection_name}")
    print(f"✅ Host: {milvus_host}:{milvus_port}")
    print(f"\n💡 Next Steps:")
    print(f"   1. Update .env: Set VECTOR_DB_TYPE=milvus")
    print(f"   2. Test RAG: python tests/test_rag_chat.py")
    print(f"   3. View in Attu: http://localhost:8000")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = migrate_faiss_to_milvus()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
