"""
Simple test to verify your Ollama Chat desktop app works with RAG
Run this to confirm everything is connected properly
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    Testing Your Ollama Chat Connection with RAG System          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

print("\n📋 Step 1: Testing Ollama Connection")
print("-" * 70)

try:
    from langchain_ollama import ChatOllama
    
    # Connect to your running Ollama Chat instance
    llm = ChatOllama(model="llama3.1", temperature=0.7)
    
    print("✅ Connected to Ollama")
    
    # Test basic functionality
    print("\n🧪 Asking Ollama a test question...")
    response = llm.invoke("Say 'I am ready!' if you can hear me")
    answer = response.content if hasattr(response, 'content') else response
    
    print(f"✅ Ollama responded: {answer}")
    
except Exception as e:
    print(f"❌ Error connecting to Ollama: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Make sure Ollama Chat desktop app is running")
    print("   2. Run: ollama list")
    print("   3. If llama3.1 is missing, run: ollama pull llama3.1")
    sys.exit(1)

print("\n📋 Step 2: Testing Vector Store")
print("-" * 70)

try:
    from src.vector_store_factory import get_vector_store
    
    vector_store = get_vector_store(dimension=384)
    vector_store.load()
    
    print(f"✅ Loaded vector store with {vector_store.total_vectors} vectors")
    
except Exception as e:
    print(f"❌ Error loading vector store: {e}")
    print("\n💡 You need to generate embeddings first!")
    print("   Open notebooks/pdf_loader.ipynb and run the cells to create the vector store")
    sys.exit(1)

print("\n📋 Step 3: Testing Embedding Manager")
print("-" * 70)

try:
    from src.embedding import EmbeddingManager
    
    embedding_manager = EmbeddingManager()
    test_embedding = embedding_manager.embed_query("test")
    
    print(f"✅ Embedding manager working (dimension: {len(test_embedding)})")
    
except Exception as e:
    print(f"❌ Error with embedding manager: {e}")
    sys.exit(1)

print("\n📋 Step 4: Testing Complete RAG Pipeline")
print("-" * 70)

try:
    # Test query
    test_query = "What is the DevOps Technical Writer Agent?"
    
    print(f"\n🔍 Query: {test_query}")
    print("\n⏳ Searching knowledge base...")
    
    # Search
    query_embedding = embedding_manager.embed_query(test_query)
    results = vector_store.search(query_embedding, top_k=3)
    
    print(f"✅ Found {len(results)} relevant chunks")
    
    # Show top result
    if results:
        top_result = results[0]
        print(f"\n📄 Top Result:")
        print(f"   Distance: {top_result['distance']:.4f}")
        print(f"   Source: {top_result['metadata'].get('source', 'Unknown')}")
        print(f"   Page: {top_result['metadata'].get('page_number', 'N/A')}")
        print(f"   Text: {top_result['metadata'].get('text', '')[:150]}...")
    
    # Generate answer with Ollama
    print(f"\n⏳ Asking your Ollama to generate answer...")
    
    context = "\n\n".join([r['metadata'].get('text', '') for r in results[:3]])
    
    prompt = f"""You are a helpful DevOps assistant. Answer based on this context:

{context}

Question: {test_query}

Answer:"""
    
    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, 'content') else response
    
    print(f"\n{'='*70}")
    print("💡 ANSWER FROM YOUR OLLAMA:")
    print('='*70)
    print(answer)
    print('='*70)
    
    print("\n✅ RAG Pipeline Working Successfully!")
    
except Exception as e:
    print(f"❌ Error in RAG pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("🎉 ALL TESTS PASSED!")
print("="*70)
print("""
Your setup is working perfectly! You can now:

1. Run interactive chat:
   python test_rag_chat.py

2. Quick single queries:
   python quick_test.py "your question"

3. Use in Jupyter notebook:
   answer = rag_simple("your question")

Your Ollama Chat desktop app and RAG system are connected! 🚀
""")
