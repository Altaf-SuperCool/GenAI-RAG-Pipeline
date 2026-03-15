"""
Quick Milvus Database Access
Provides interactive access to your Milvus vector database
"""
from pymilvus import connections, Collection, utility
import sys

def main():
    print("=" * 70)
    print("  Milvus Database Access")
    print("=" * 70)
    
    # Connect
    print("\n🔌 Connecting to Milvus...")
    try:
        connections.connect(
            alias="default",
            host="localhost",
            port=19530
        )
        print("   ✅ Connected successfully!")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n   Make sure Milvus is running:")
        print("   $ docker-compose up -d")
        sys.exit(1)
    
    # Get server info
    try:
        version = utility.get_server_version()
        print(f"   Server version: {version}")
    except:
        pass
    
    # List collections
    print("\n📚 Collections:")
    try:
        collections = utility.list_collections()
        
        if not collections:
            print("   No collections found.")
            print("\n   To create a collection, run:")
            print("   $ python scripts/migrate_faiss_to_milvus.py")
            sys.exit(0)
        
        print(f"   Found {len(collections)} collection(s):\n")
        
        for coll_name in collections:
            coll = Collection(coll_name)
            coll.load()
            print(f"   📊 {coll_name}")
            print(f"      Vectors: {coll.num_entities:,}")
            print(f"      Loaded: {coll.is_loaded}")
            print(f"      Has Index: {coll.has_index()}")
            print()
            
    except Exception as e:
        print(f"   ❌ Error listing collections: {e}")
        sys.exit(1)
    
    # Access main collection
    collection_name = "devops_knowledgebase"
    if collection_name in collections:
        print(f"\n🔍 Accessing '{collection_name}':")
        
        try:
            collection = Collection(collection_name)
            collection.load()
            
            # Schema
            print(f"\n   Schema:")
            for field in collection.schema.fields:
                print(f"      • {field.name} ({field.dtype})")
            
            # Sample data
            if collection.num_entities > 0:
                print(f"\n   Sample records (first 3):")
                results = collection.query(
                    expr="",
                    output_fields=["text", "source", "chunk_id"],
                    limit=3
                )
                
                for i, record in enumerate(results, 1):
                    print(f"\n   Record {i}:")
                    print(f"      ID: {record.get('id', 'N/A')}")
                    print(f"      Source: {record.get('source', 'N/A')}")
                    print(f"      Chunk ID: {record.get('chunk_id', 'N/A')}")
                    text = record.get('text', 'N/A')
                    if len(text) > 150:
                        text = text[:150] + "..."
                    print(f"      Text: {text}")
            else:
                print(f"\n   ⚠️  Collection is empty")
                
        except Exception as e:
            print(f"   ❌ Error accessing collection: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("  Access Methods")
    print("=" * 70)
    print("\n✅ 1. Web UI (Attu): http://localhost:8000")
    print("      → Visual interface for browsing and searching")
    print("\n✅ 2. Python API:")
    print("      from pymilvus import connections, Collection")
    print("      connections.connect('default', host='localhost', port=19530)")
    print("      collection = Collection('devops_knowledgebase')")
    print("      collection.load()")
    print("\n✅ 3. RAG Vector Store:")
    print("      from src.vector_store_factory import get_vector_store")
    print("      store = get_vector_store(store_type='milvus')")
    print("\n" + "=" * 70)
    
    # Cleanup
    connections.disconnect("default")
    print("\n✅ Disconnected from Milvus")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
