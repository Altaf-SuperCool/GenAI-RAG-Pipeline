"""
Clear Milvus Collection
Drops and recreates the Milvus collection for a fresh start
"""
from pymilvus import connections, utility, Collection
import os
from dotenv import load_dotenv

load_dotenv()

def clear_milvus():
    """Drop and recreate Milvus collection"""
    
    print("=" * 70)
    print("  Clear Milvus Collection")
    print("=" * 70)
    
    # Connect
    print("\n🔌 Connecting to Milvus...")
    host = os.getenv("MILVUS_HOST", "localhost")
    port = int(os.getenv("MILVUS_PORT", "19530"))
    collection_name = os.getenv("MILVUS_COLLECTION_NAME", "devops_knowledgebase")
    
    try:
        connections.connect("default", host=host, port=port)
        print(f"   ✅ Connected to {host}:{port}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Check if collection exists
    if utility.has_collection(collection_name):
        print(f"\n📊 Current state:")
        collection = Collection(collection_name)
        print(f"   Collection: {collection_name}")
        print(f"   Vectors: {collection.num_entities}")
        
        # Confirm deletion
        print(f"\n⚠️  Warning: This will DELETE all {collection.num_entities} vectors!")
        response = input(f"   Type 'yes' to confirm deletion: ")
        
        if response.lower() == 'yes':
            print(f"\n🗑️  Dropping collection '{collection_name}'...")
            utility.drop_collection(collection_name)
            print(f"   ✅ Collection dropped successfully")
            
            print("\n" + "=" * 70)
            print("  Collection Cleared!")
            print("=" * 70)
            print(f"\n💡 Next Steps:")
            print(f"   1. Index PDFs into Milvus:")
            print(f"      python src/indexing/pdf_indexer.py")
            print(f"   2. Or run migration from FAISS:")
            print(f"      python scripts/migrate_faiss_to_milvus.py")
            print("=" * 70)
            return True
        else:
            print("\n   ❌ Deletion cancelled")
            return False
    else:
        print(f"\n   ℹ️  Collection '{collection_name}' does not exist")
        print(f"   Nothing to clear")
        return True
    
    connections.disconnect("default")


if __name__ == "__main__":
    try:
        clear_milvus()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
