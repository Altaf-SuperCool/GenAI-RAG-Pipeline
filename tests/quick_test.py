"""Quick RAG Query Tester - Single query testing"""

import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.vector_store_factory import get_vector_store
from src.embedding import EmbeddingManager
from langchain_ollama import ChatOllama

load_dotenv()

def quick_test(query: str, show_sources: bool = True):
    """Quick test a single query"""
    print(f"\n{'='*70}")
    print(f"📝 Testing Query: {query}")
    print('='*70)
    
    try:
        # Initialize
        print("\n🔧 Initializing components...")
        embedding_manager = EmbeddingManager()
        vector_store = get_vector_store(dimension=384)
        vector_store.load()
        
        print(f"✅ Loaded {vector_store.total_vectors} vectors from knowledge base")
        
        # Search
        print(f"\n🔍 Searching for relevant context...")
        query_embedding = embedding_manager.embed_query(query)
        results = vector_store.search(query_embedding, top_k=3)
        
        print(f"✅ Found {len(results)} relevant chunks")
        
        if show_sources:
            print(f"\n📚 Top Results:")
            for i, r in enumerate(results, 1):
                print(f"\n  {i}. Distance: {r['distance']:.4f}")
                print(f"     Source: {r['metadata'].get('source', 'Unknown')}")
                print(f"     Page: {r['metadata'].get('page_number', 'N/A')}")
                print(f"     Text: {r['metadata'].get('text', '')[:150]}...")
        
        # Generate answer
        print(f"\n🤖 Generating answer with Ollama llama3.1...")
        context = "\n\n".join([r['metadata'].get('text', '') for r in results])
        
        llm = ChatOllama(model="llama3.1", temperature=0.7)
        
        prompt = f"""You are a helpful DevOps knowledgebase assistant. Answer the question based on the provided context.

Context:
{context}

Question: {query}

Answer: Provide a clear, concise answer based on the context above."""
        
        response = llm.invoke(prompt)
        answer = response if isinstance(response, str) else response.content
        
        print(f"\n{'='*70}")
        print("💡 ANSWER:")
        print('='*70)
        print(answer)
        print('='*70)
        
    except FileNotFoundError:
        print("\n❌ Error: Vector store not found!")
        print("Please run document ingestion first in your Jupyter notebook.")
        print("Open notebooks/pdf_loader.ipynb and run the cells to generate embeddings.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Default test query
        query = "What is the DevOps Technical Writer Agent?"
        print("\n💡 No query provided, using default test query")
    
    quick_test(query, show_sources=True)
    
    print("\n\n📝 Usage Examples:")
    print("  python quick_test.py")
    print("  python quick_test.py How do CI/CD pipelines work?")
    print("  python quick_test.py What are microservices?")
