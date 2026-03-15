"""
Simple Command-Line RAG Chat
Fastest way to test - no web interface overhead
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

print("=" * 70)
print("  Simple RAG Chat - Command Line")
print("=" * 70)

# Load components
print("\n⏳ Loading components...")

try:
    from src.vector_store_factory import get_vector_store
    from src.embedding import EmbeddingManager
    from langchain_ollama import ChatOllama
    
    print("   Loading vector store...")
    vector_store = get_vector_store()
    vector_store.load()
    print(f"   ✅ Loaded {vector_store.total_vectors:,} vectors")
    
    print("   Loading embedding model...")
    embedding_manager = EmbeddingManager()
    print(f"   ✅ Embedding dimension: {embedding_manager.dimension}")
    
    print("   Connecting to Ollama...")
    llm = ChatOllama(model="llama3.1", temperature=0.7)
    llm.invoke("test")  # Quick connection test
    print("   ✅ Connected to Ollama")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("  1. Ollama Desktop is running")
    print("  2. Vector store exists (run: python src/indexing/pdf_indexer.py)")
    print("  3. Model llama3.1 is available (run: ollama list)")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ Ready! Type your questions (or 'quit' to exit)")
print("=" * 70)
print("\n💡 Quick commands: 'stats', 'help', 'quit'\n")

# Chat loop
while True:
    try:
        # Get question
        question = input("\n🙋 You: ").strip()
        
        if not question:
            continue
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if question.lower() == 'stats':
            print(f"\n📊 System Stats:")
            print(f"   Vectors: {vector_store.total_vectors:,}")
            print(f"   Dimension: {embedding_manager.dimension}")
            print(f"   Vector DB: FAISS")
            print(f"   LLM: llama3.1")
            continue
        
        if question.lower() == 'help':
            print("\n💡 How to use:")
            print("   - Just type your question and press Enter")
            print("   - Type 'stats' to see system info")
            print("   - Type 'quit' to exit")
            print("\n   Example questions:")
            print("   • What is the platform architecture?")
            print("   • Tell me about DevOps tools")
            print("   • Explain the deployment process")
            continue
        
        # Search
        print("\n🔍 Searching...")
        query_embedding = embedding_manager.embed_query(question)
        results = vector_store.search(query_embedding, top_k=3)
        
        if not results:
            print("❌ No relevant documents found.")
            continue
        
        # Generate answer
        print("🤖 Generating answer...")
        
        context = "\n\n".join([
            f"[{r['metadata'].get('source', 'Unknown').split('/')[-1].split('\\')[-1]}]\n{r['metadata'].get('text', r['metadata'].get('content', ''))[:400]}"
            for r in results
        ])
        
        prompt = f"""Answer based on this context:

{context}

Question: {question}

Answer:"""
        
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        # Display answer
        print("\n" + "=" * 70)
        print("💡 Answer:")
        print("=" * 70)
        print(answer)
        
        # Display sources
        print("\n📚 Sources:")
        for i, r in enumerate(results, 1):
            source = r['metadata'].get('source', 'Unknown').split('/')[-1].split('\\')[-1]
            conf = max(0, 100 - (r.get('distance', 0) * 100))
            print(f"   {i}. {source} ({conf:.0f}% match)")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Try again or type 'quit' to exit.")
