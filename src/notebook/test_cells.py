# Quick Test Cells for Jupyter Notebook
# Copy these cells to test your RAG system with Ollama

## ============================================================================
## TEST CELL 1: Simple Single Query Test
## ============================================================================

# Simple one-line test
test_query = "What is the DevOps Technical Writer Agent?"
answer = rag_simple(test_query)
print(f"Q: {test_query}\n\nA: {answer}")


## ============================================================================
## TEST CELL 2: Multiple Query Test
## ============================================================================

# Test multiple queries at once
test_queries = [
    "What is the DevOps Technical Writer Agent?",
    "How do CI/CD pipelines work?",
    "Best practices for Kubernetes deployment",
    "Explain microservices architecture"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"Test {i}: {query}")
    print('='*70)
    answer = rag_simple(query)
    print(f"\n{answer}\n")


## ============================================================================
## TEST CELL 3: Advanced Query with Sources
## ============================================================================

# Test with full details including sources
test_query = "How do I troubleshoot Kubernetes pod failures?"

result = rag_advanced(test_query)

print("=" * 70)
print("QUESTION:")
print("=" * 70)
print(test_query)

print("\n" + "=" * 70)
print("ANSWER:")
print("=" * 70)
print(result['answer'])

print("\n" + "=" * 70)
print("CONFIDENCE SCORE:")
print("=" * 70)
print(f"{result['confidence']:.3f}")

print("\n" + "=" * 70)
print("SOURCES:")
print("=" * 70)
for i, source in enumerate(result['sources'][:3], 1):
    print(f"{i}. {source}")


## ============================================================================
## TEST CELL 4: Interactive Loop (Run to chat continuously)
## ============================================================================

def interactive_test():
    """Interactive testing loop"""
    print("\n" + "="*70)
    print("Interactive RAG Testing")
    print("Type 'quit' to stop")
    print("="*70)
    
    while True:
        query = input("\n❓ Your question: ").strip()
        
        if not query:
            continue
            
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        print("\n" + "-"*70)
        try:
            answer = rag_simple(query)
            print(f"💡 {answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-"*70)

# Run interactive test
interactive_test()


## ============================================================================
## TEST CELL 5: Performance Benchmark
## ============================================================================

import time

test_queries = [
    "What is DevOps?",
    "CI/CD best practices",
    "Kubernetes architecture",
    "Docker vs containers",
    "Microservices benefits"
]

print("=" * 70)
print("Performance Benchmark")
print("=" * 70)

total_time = 0
for i, query in enumerate(test_queries, 1):
    start = time.time()
    answer = rag_simple(query)
    elapsed = time.time() - start
    total_time += elapsed
    
    print(f"\n{i}. Query: {query}")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Answer: {answer[:100]}...")

print(f"\n{'='*70}")
print(f"Total time: {total_time:.2f}s")
print(f"Average time per query: {total_time/len(test_queries):.2f}s")
print(f"{'='*70}")


## ============================================================================
## TEST CELL 6: Compare Different LLMs
## ============================================================================

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

test_query = "What are the benefits of microservices?"

# Get context
query_embedding = embedding_manager.embed_query(test_query)
results = vector_store.search(query_embedding, top_k=3)
context = "\n\n".join([r['metadata'].get('text', '') for r in results])

prompt_template = f"""Answer based on this context:

{context}

Question: {test_query}

Answer:"""

print("=" * 70)
print("Comparing LLM Responses")
print("=" * 70)
print(f"\nQuery: {test_query}\n")

# Ollama
print("\n" + "="*70)
print("🦙 OLLAMA (llama3.1)")
print("="*70)
llm_ollama = ChatOllama(model="llama3.1", temperature=0.7)
response = llm_ollama.invoke(prompt_template)
answer = response if isinstance(response, str) else response.content
print(answer)

# Groq (if API key available)
try:
    print("\n" + "="*70)
    print("⚡ GROQ (gemma2-9b-it)")
    print("="*70)
    llm_groq = ChatGroq(model="gemma2-9b-it", temperature=0.7)
    response = llm_groq.invoke(prompt_template)
    print(response.content)
except Exception as e:
    print(f"Groq not available: {e}")


## ============================================================================
## TEST CELL 7: Check System Status
## ============================================================================

# Check all components
print("=" * 70)
print("System Status Check")
print("=" * 70)

# Vector store
try:
    stats = vector_store.get_stats()
    print("\n✅ Vector Store:")
    print(f"   Type: {stats['type']}")
    print(f"   Total Vectors: {stats['total_vectors']}")
    print(f"   Dimension: {stats['dimension']}")
except Exception as e:
    print(f"\n❌ Vector Store Error: {e}")

# Embedding Manager
try:
    test_embedding = embedding_manager.embed_query("test")
    print("\n✅ Embedding Manager:")
    print(f"   Model: {embedding_manager.model_name}")
    print(f"   Embedding dimension: {len(test_embedding)}")
except Exception as e:
    print(f"\n❌ Embedding Manager Error: {e}")

# LLM
try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.1")
    response = llm.invoke("Say 'OK' if you're working")
    print("\n✅ Ollama LLM:")
    print(f"   Model: llama3.1")
    print(f"   Status: Working")
    print(f"   Response: {response if isinstance(response, str) else response.content}")
except Exception as e:
    print(f"\n❌ Ollama Error: {e}")

print("\n" + "=" * 70)


## ============================================================================
## TEST CELL 8: Sample Queries by Category
## ============================================================================

# Test different types of questions
categories = {
    "Technical": [
        "How does Kubernetes cluster work?",
        "What is a Docker container?"
    ],
    "Conceptual": [
        "Benefits of DevOps culture",
        "Why use microservices?"
    ],
    "Process": [
        "Steps to deploy an application",
        "How to set up CI/CD pipeline?"
    ],
    "Troubleshooting": [
        "How to debug pod failures?",
        "Troubleshooting Docker network issues"
    ]
}

for category, queries in categories.items():
    print("\n" + "=" * 70)
    print(f"Category: {category}")
    print("=" * 70)
    
    for query in queries:
        print(f"\nQ: {query}")
        try:
            answer = rag_simple(query)
            print(f"A: {answer[:200]}...")  # First 200 chars
        except Exception as e:
            print(f"Error: {e}")
