"""
Performance test for RAG system components
Helps identify where slowdowns are occurring
"""
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vector_store_factory import get_vector_store
from src.embedding import EmbeddingManager
from langchain_ollama import ChatOllama

print("=" * 70)
print("Performance Test - RAG System Components")
print("=" * 70)

# Test query
test_query = "What is DevOps?"

# Test 1: Vector Store Loading
print("\n📦 Test 1: Vector Store Loading")
start = time.time()
vector_store = get_vector_store()
vector_store.load()
load_time = time.time() - start
print(f"   Time: {load_time:.2f}s")
print(f"   Vectors loaded: {vector_store.total_vectors}")

# Test 2: Embedding Manager Initialization
print("\n🔤 Test 2: Embedding Manager Initialization")
start = time.time()
embedding_manager = EmbeddingManager()
init_time = time.time() - start
print(f"   Time: {init_time:.2f}s")
print(f"   Dimension: {embedding_manager.dimension}")

# Test 3: Query Embedding
print("\n🔍 Test 3: Query Embedding Generation")
start = time.time()
query_embedding = embedding_manager.embed_query(test_query)
embed_time = time.time() - start
print(f"   Time: {embed_time:.2f}s")
print(f"   Query: '{test_query}'")

# Test 4: Vector Search (different top_k values)
print("\n🔎 Test 4: Vector Search Performance")
for k in [3, 5, 10]:
    start = time.time()
    results = vector_store.search(query_embedding, top_k=k)
    search_time = time.time() - start
    print(f"   top_k={k}: {search_time:.3f}s ({len(results)} results)")

# Test 5: LLM Response Generation
print("\n🤖 Test 5: LLM Response Generation")
try:
    llm = ChatOllama(
        model="llama3.1",
        temperature=0.3,
        num_predict=512,
        base_url="http://localhost:11434"
    )
    
    # Get some context
    results = vector_store.search(query_embedding, top_k=3)
    context = "\n\n".join([
        f"{chunk['metadata'].get('text', chunk['metadata'].get('content', ''))[:500]}..."
        for chunk in results
    ])
    
    prompt = f"""Based on this context, answer concisely:

{context}

Q: {test_query}
A:"""
    
    # First call (cold start)
    print("\n   First call (cold start):")
    start = time.time()
    response = llm.invoke(prompt)
    first_time = time.time() - start
    print(f"   Time: {first_time:.2f}s")
    print(f"   Response length: {len(response.content)} chars")
    
    # Second call (warm)
    print("\n   Second call (warm):")
    start = time.time()
    response = llm.invoke("What is Python?")
    second_time = time.time() - start
    print(f"   Time: {second_time:.2f}s")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Make sure Ollama is running!")

# Summary
print("\n" + "=" * 70)
print("📊 Performance Summary")
print("=" * 70)
print(f"Vector Store Load:    {load_time:.2f}s")
print(f"Embedding Init:       {init_time:.2f}s")
print(f"Query Embedding:      {embed_time:.3f}s")
print(f"Vector Search (k=3):  ~{search_time:.3f}s")
try:
    print(f"LLM Cold Start:       {first_time:.2f}s")
    print(f"LLM Warm Call:        {second_time:.2f}s")
    print(f"\nTotal for one query:  ~{embed_time + search_time + second_time:.2f}s")
except:
    print(f"\nTotal for search:     ~{embed_time + search_time:.3f}s (LLM not tested)")

print("\n💡 Optimization Tips:")
print("   - Embedding: Should be < 0.1s")
print("   - Search: Should be < 0.05s") 
print("   - LLM: 2-5s is normal, 10s+ may indicate issues")
print("   - Check Ollama model is loaded (ollama list)")
print("=" * 70)
