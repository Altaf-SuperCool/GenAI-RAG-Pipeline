# Testing RAG System with Ollama Chat

## 🎯 Quick Testing Guide

This guide shows you how to test your DevOps Knowledgebase RAG system using Ollama.

---

## ⚡ QUICK START: You Have Ollama Chat Running?

If you already have the **Ollama Chat desktop app** running on your PC:

### 1. Test Your Connection
```powershell
cd "C:\Users\v193570\Documents\Agentic AI\Agentic_RAG"
python test_ollama_connection.py
```

This will verify that your Ollama Chat app works with your RAG system!

### 2. Start Asking Questions
```powershell
# Interactive chat
python test_rag_chat.py

# Single query
python quick_test.py "What is DevOps?"
```

**Your Ollama Chat app and RAG system share the same Ollama engine!**

📖 See [USING_OLLAMA_CHAT_APP.md](USING_OLLAMA_CHAT_APP.md) for detailed guide on using your desktop Ollama Chat with RAG.

---

## 🚀 Method 1: Interactive Chat Script (Recommended)

### Step 1: Create Interactive Chat Script

Save this as `test_rag_chat.py`:

```python
"""
Interactive RAG Chat Tester
Test your RAG system with Ollama in a chat-like interface
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.vector_store_factory import get_vector_store
from src.embedding import EmbeddingManager
from langchain_ollama import ChatOllama

# Load environment
load_dotenv()

class RAGChatTester:
    """Interactive RAG chat interface for testing"""
    
    def __init__(self):
        print("🚀 Initializing RAG Chat Tester...")
        print("=" * 70)
        
        # Initialize components
        self.embedding_manager = EmbeddingManager()
        self.vector_store = get_vector_store(dimension=384)
        
        # Load existing vector store
        try:
            self.vector_store.load()
            print(f"✅ Loaded {self.vector_store.total_vectors} vectors")
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            print("Make sure you have generated embeddings first!")
            sys.exit(1)
        
        # Initialize Ollama
        self.llm = ChatOllama(
            model="llama3.1",
            temperature=0.7
        )
        print("✅ Ollama llama3.1 ready")
        print("=" * 70)
        print()
    
    def search_context(self, query: str, top_k: int = 5):
        """Search for relevant context"""
        # Generate query embedding
        query_embedding = self.embedding_manager.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        return results
    
    def generate_answer(self, query: str, context: str):
        """Generate answer using Ollama"""
        prompt = f"""You are a helpful DevOps knowledgebase assistant. Answer the question based on the provided context.

Context:
{context}

Question: {query}

Answer: Provide a clear, concise answer based on the context above. If the context doesn't contain relevant information, say so."""

        # Generate response
        response = self.llm.invoke(prompt)
        
        # Handle both string and object responses
        if isinstance(response, str):
            return response
        else:
            return response.content
    
    def chat_query(self, query: str, show_sources: bool = True):
        """Process a single query and return answer with sources"""
        print(f"\n🔍 Query: {query}")
        print("-" * 70)
        
        # Search
        print("Searching knowledge base...")
        results = self.search_context(query, top_k=5)
        
        if not results:
            print("❌ No relevant documents found")
            return
        
        print(f"✅ Found {len(results)} relevant chunks")
        
        # Build context
        context = "\n\n".join([
            f"[Source {i+1}] {r['metadata'].get('text', '')[:500]}..."
            for i, r in enumerate(results[:3])
        ])
        
        # Generate answer
        print("Generating answer with Ollama...")
        answer = self.generate_answer(query, context)
        
        # Display results
        print("\n" + "=" * 70)
        print("💡 ANSWER:")
        print("=" * 70)
        print(answer)
        print()
        
        if show_sources:
            print("=" * 70)
            print("📚 SOURCES:")
            print("=" * 70)
            for i, result in enumerate(results[:3], 1):
                meta = result['metadata']
                print(f"\n{i}. Distance: {result['distance']:.4f}")
                print(f"   Source: {meta.get('source', 'Unknown')}")
                print(f"   Page: {meta.get('page_number', 'N/A')}")
                print(f"   Preview: {meta.get('text', '')[:200]}...")
        
        print("\n" + "=" * 70)
    
    def run_interactive(self):
        """Run interactive chat loop"""
        print("\n🎉 RAG Chat Tester Ready!")
        print("=" * 70)
        print("Commands:")
        print("  - Type your question to get an answer")
        print("  - Type 'quit' or 'exit' to stop")
        print("  - Type 'help' to see commands")
        print("  - Type 'stats' to see system stats")
        print("=" * 70)
        
        while True:
            try:
                # Get user input
                query = input("\n❓ Your question: ").strip()
                
                if not query:
                    continue
                
                # Handle commands
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                elif query.lower() == 'help':
                    print("\n📖 Available Commands:")
                    print("  quit/exit - Exit the chat")
                    print("  stats - Show system statistics")
                    print("  help - Show this help message")
                    print("  <your question> - Ask anything from the knowledge base")
                    continue
                
                elif query.lower() == 'stats':
                    stats = self.vector_store.get_stats()
                    print("\n📊 System Statistics:")
                    print(f"  Total Vectors: {stats['total_vectors']}")
                    print(f"  Dimension: {stats['dimension']}")
                    print(f"  Type: {stats['type']}")
                    continue
                
                # Process query
                self.chat_query(query, show_sources=True)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.")


def main():
    """Main function"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         DevOps Knowledgebase - RAG Chat Tester                      ║
║         Interactive testing with Ollama                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create and run chat tester
    tester = RAGChatTester()
    tester.run_interactive()


if __name__ == "__main__":
    main()
```

### Step 2: Run Interactive Chat

```bash
cd "C:\Users\v193570\Documents\Agentic AI\Agentic_RAG"
python test_rag_chat.py
```

### Step 3: Test Your Queries

```
❓ Your question: What is the DevOps Technical Writer Agent?

🔍 Query: What is the DevOps Technical Writer Agent?
----------------------------------------------------------------------
Searching knowledge base...
✅ Found 5 relevant chunks
Generating answer with Ollama...

======================================================================
💡 ANSWER:
======================================================================
The DevOps Technical Writer Agent is optimized for operational 
documentation and can ingest content from files or knowledge systems 
to synthesize production-ready SOPs, runbooks, and supporting artifacts.

======================================================================
📚 SOURCES:
======================================================================

1. Distance: 0.1234
   Source: PLAT_Confluence.pdf
   Page: 306
   Preview: The DevOps Technical Writer Agent is optimized for...

======================================================================
```

---

## 🎮 Method 2: Direct Jupyter Notebook Testing

If you're already in your notebook (`pdf_loader.ipynb`), add this test cell:

```python
# Test Cell: Interactive RAG Chat
def test_rag_chat():
    """Quick test function for notebook"""
    print("=" * 70)
    print("RAG System Test")
    print("=" * 70)
    
    # Test queries
    test_queries = [
        "What is the DevOps Technical Writer Agent?",
        "How do CI/CD pipelines work?",
        "Best practices for Kubernetes deployment",
        "Explain microservices architecture"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*70}")
        print(f"Test {i}: {query}")
        print('='*70)
        
        # Use your existing rag_simple function
        answer = rag_simple(query)
        print(f"\nAnswer:\n{answer}")
        
        # Or use rag_advanced for more details
        # result = rag_advanced(query)
        # print(f"\nAnswer: {result['answer']}")
        # print(f"Confidence: {result['confidence']}")
        # print(f"\nSources:")
        # for source in result['sources'][:3]:
        #     print(f"  - {source}")

# Run test
test_rag_chat()
```

---

## 🔧 Method 3: Single Query Tester

For quick one-off tests, create `quick_test.py`:

```python
"""Quick RAG Query Tester"""

import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.vector_store_factory import get_vector_store
from src.embedding import EmbeddingManager
from langchain_ollama import ChatOllama
import numpy as np

load_dotenv()

def quick_test(query: str):
    """Quick test a single query"""
    print(f"\n{'='*70}")
    print(f"Testing: {query}")
    print('='*70)
    
    # Initialize
    embedding_manager = EmbeddingManager()
    vector_store = get_vector_store(dimension=384)
    vector_store.load()
    
    # Search
    query_embedding = embedding_manager.embed_query(query)
    results = vector_store.search(query_embedding, top_k=3)
    
    print(f"\n✅ Found {len(results)} results:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. Distance: {r['distance']:.4f}")
        print(f"   Text: {r['metadata'].get('text', '')[:150]}...")
    
    # Generate answer
    context = "\n\n".join([r['metadata'].get('text', '') for r in results])
    
    llm = ChatOllama(model="llama3.1", temperature=0.7)
    
    prompt = f"""Answer based on this context:

{context}

Question: {query}

Answer:"""
    
    print(f"\n{'='*70}")
    print("Generating answer with Ollama...")
    print('='*70)
    
    response = llm.invoke(prompt)
    answer = response if isinstance(response, str) else response.content
    
    print(f"\n💡 Answer:\n{answer}")
    print('='*70)

if __name__ == "__main__":
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "What is the DevOps Technical Writer Agent?"
    
    quick_test(query)
```

**Usage:**
```bash
# Default query
python quick_test.py

# Custom query
python quick_test.py "How do I deploy microservices?"
```

---

## 🌐 Method 4: Using Existing Notebook Functions

In your `pdf_loader.ipynb`, you already have these functions:

### Simple Test:
```python
# Test with simple RAG
answer = rag_simple("What is the DevOps Technical Writer Agent?")
print(answer)
```

### Advanced Test with Sources:
```python
# Test with advanced RAG
result = rag_advanced("How do CI/CD pipelines work?")

print(f"Answer: {result['answer']}")
print(f"\nConfidence: {result['confidence']}")
print(f"\nSources:")
for source in result['sources']:
    print(f"  - {source}")
```

### Multiple Queries Test:
```python
# Test multiple queries
queries = [
    "What is Kubernetes?",
    "Best practices for Docker containers",
    "How to set up CI/CD pipeline?",
    "Microservices architecture benefits"
]

for query in queries:
    print(f"\n{'='*70}")
    print(f"Q: {query}")
    print('='*70)
    answer = rag_simple(query)
    print(f"A: {answer}\n")
```

---

## 🎯 Method 5: Ollama Direct Testing (No RAG)

To test Ollama itself without RAG:

```python
from langchain_ollama import ChatOllama

# Initialize Ollama
llm = ChatOllama(model="llama3.1", temperature=0.7)

# Test direct query
response = llm.invoke("Tell me about DevOps in 2 sentences")
print(response.content if hasattr(response, 'content') else response)
```

---

## 📊 Comparison of Methods

| Method | Best For | Complexity | Output |
|--------|----------|------------|--------|
| **Interactive Chat** | Continuous testing | Medium | Full details + chat loop |
| **Notebook Cells** | Quick inline tests | Low | Simple answers |
| **Quick Test Script** | Single queries | Low | Fast results |
| **Command Line** | Automation | Low | Scriptable |
| **Direct Ollama** | LLM testing only | Very Low | No RAG retrieval |

---

## 🔍 Recommended Testing Workflow

### 1. First Time Setup
```bash
# Navigate to project
cd "C:\Users\v193570\Documents\Agentic AI\Agentic_RAG"

# Create test script (copy from Method 1 above)
# Save as test_rag_chat.py

# Run interactive chat
python test_rag_chat.py
```

### 2. Quick Tests
```python
# In Jupyter notebook
answer = rag_simple("your question here")
print(answer)
```

### 3. Detailed Analysis
```python
# In Jupyter notebook
result = rag_advanced("your question here")
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Sources: {result['sources']}")
```

---

## 💡 Sample Test Queries

Try these queries to test your system:

### Technical Questions
```
- "What is the DevOps Technical Writer Agent?"
- "How do CI/CD pipelines work?"
- "Best practices for Kubernetes deployment"
- "Explain microservices architecture"
- "How to configure Docker containers?"
```

### Conceptual Questions
```
- "Benefits of using AI for documentation"
- "DevOps vs traditional deployment"
- "Cloud vs on-premises infrastructure"
```

### Specific Questions
```
- "How to troubleshoot pod failures in Kubernetes?"
- "Steps to set up automated testing"
- "Security best practices for production"
```

---

## 🐛 Troubleshooting

### Issue: "Ollama not responding"
**Solution:**
```bash
# Check if Ollama is running
ollama list

# Pull llama3.1 model
ollama pull llama3.1

# Test directly
ollama run llama3.1 "Hello"
```

### Issue: "No vectors found"
**Solution:**
```python
# Check vector store
from src.vector_store_factory import get_vector_store
store = get_vector_store(dimension=384)
store.load()
print(f"Total vectors: {store.total_vectors}")

# If 0, you need to run document ingestion first
```

### Issue: "Slow responses"
**Solution:**
- Reduce `top_k` from 5 to 3
- Use Groq instead: Change LLM to ChatGroq
- Check system resources (RAM, CPU)

---

## ✅ Next Steps

1. **Start with Interactive Chat** (Method 1)
   - Most user-friendly
   - See full conversation flow
   - Easy to test multiple queries

2. **Move to Notebook** for development
   - Use `rag_simple()` for quick checks
   - Use `rag_advanced()` for detailed analysis

3. **Create Custom Tests** as needed
   - Batch testing with scripts
   - Automated testing for regression
   - Performance benchmarking

---

## 🎉 Quick Win

Try this right now in your notebook:

```python
# Single cell test
print("Testing RAG with Ollama...")
test_query = "What is the DevOps Technical Writer Agent?"
answer = rag_simple(test_query)
print(f"\nQ: {test_query}")
print(f"A: {answer}")
```

That's it! You're testing with Ollama! 🚀
