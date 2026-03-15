"""
Interactive RAG Chat Tester
Test your RAG system with Ollama in a chat-like interface
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

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
