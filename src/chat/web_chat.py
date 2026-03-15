"""
Web-based Chat Interface for RAG System
Launch this to get a desktop-like chat experience in your browser
"""
import os
import sys
import gradio as gr
from sentence_transformers import SentenceTransformer

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.vector_store_factory import get_vector_store
from src.embedding import EmbeddingManager

# Try to import Ollama
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  langchain-ollama not installed. Install with: pip install langchain-ollama")

# Initialize components
print("🔧 Initializing RAG system...")
vector_store = None
embedding_manager = None
llm = None

def initialize_rag():
    """Initialize RAG components"""
    global vector_store, embedding_manager, llm
    
    try:
        # Load vector store
        print("   Loading vector store...")
        vector_store = get_vector_store()
        vector_store.load()
        print(f"   ✅ Loaded {vector_store.total_vectors} vectors")
        
        # Initialize embedding manager
        print("   Loading embedding model...")
        embedding_manager = EmbeddingManager()
        print(f"   ✅ Embedding dimension: {embedding_manager.dimension}")
        
        # Initialize LLM
        if OLLAMA_AVAILABLE:
            print("   Connecting to Ollama...")
            llm = ChatOllama(
                model="llama3.1",
                temperature=0.3,  # Lower temperature for faster, more focused responses
                num_predict=512,  # Limit response length for speed
                base_url="http://localhost:11434"
            )
            # Test connection
            llm.invoke("test")
            print("   ✅ Connected to Ollama")
        else:
            print("   ⚠️  Ollama not available")
        
        return True
    except Exception as e:
        print(f"   ❌ Error initializing: {e}")
        return False

def search_documents(query, top_k=5):
    """Search for relevant documents"""
    if not vector_store or not embedding_manager:
        return []
    
    try:
        query_embedding = embedding_manager.embed_query(query)
        results = vector_store.search(query_embedding, top_k=top_k)
        return results
    except Exception as e:
        print(f"Error searching: {e}")
        return []

def generate_answer(query, context_chunks):
    """Generate answer using Ollama"""
    if not llm or not OLLAMA_AVAILABLE:
        return "❌ Ollama not available. Make sure Ollama Desktop is running."
    
    # Build context - limit chunk size for faster processing
    context = "\n\n".join([
        f"[Source: {chunk['metadata'].get('source', 'Unknown')}]\n{chunk['metadata'].get('text', chunk['metadata'].get('content', ''))[:500]}..."
        for chunk in context_chunks
    ])
    
    # Shorter, more focused prompt for faster responses
    prompt = f"""Based on this context, answer concisely:

{context}

Q: {query}
A:"""
    
    try:
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        return answer
    except Exception as e:
        return f"❌ Error generating answer: {e}\n\nMake sure your Ollama Desktop app is running."

def format_sources(results):
    """Format source information"""
    if not results:
        return "No sources found."
    
    sources_text = "📚 **Sources:**\n\n"
    for i, result in enumerate(results, 1):  # Show all results (now only 3)
        source = result['metadata'].get('source', 'Unknown')
        # Extract just filename
        if '\\' in source or '/' in source:
            source = source.split('\\')[-1].split('/')[-1]
        
        distance = result.get('distance', 0)
        confidence = max(0, 100 - (distance * 100))
        
        text_preview = result['metadata'].get('text', result['metadata'].get('content', ''))[:150]  # Reduced preview
        
        sources_text += f"{i}. **{source}** (Confidence: {confidence:.1f}%)\n"
        sources_text += f"   _{text_preview}..._\n\n"
    
    return sources_text

def chat_with_rag(message, history):
    """Main chat function"""
    if not message.strip():
        return history
    
    # Special commands
    if message.lower() == "stats":
        stats_msg = f"""📊 **System Statistics:**
        
- Total Vectors: {vector_store.total_vectors if vector_store else 0}
- Embedding Dimension: {embedding_manager.dimension if embedding_manager else 0}
- Vector DB: FAISS
- LLM: llama3.1 (via Ollama Desktop)
- Status: {'✅ Online' if OLLAMA_AVAILABLE and llm else '⚠️ Ollama Offline'}
"""
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": stats_msg})
        return history
    
    if message.lower() in ["help", "commands"]:
        help_msg = """💡 **Available Commands:**

- Type any question to search your documents
- `stats` - Show system statistics
- `help` - Show this help message

**Example Questions:**
- What is the platform architecture?
- Tell me about DevOps tools
- What documentation do we have?
"""
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": help_msg})
        return history
    
    # Search for relevant documents
    try:
        # Reduced top_k from 5 to 3 for faster processing
        results = search_documents(message, top_k=3)
        
        if not results:
            response = "❌ No relevant documents found. Try rephrasing your question."
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            return history
        
        # Generate answer
        answer = generate_answer(message, results)
        
        # Format sources
        sources = format_sources(results)
        
        # Combine answer and sources
        full_response = f"{answer}\n\n---\n\n{sources}"
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": full_response})
        return history
    
    except Exception as e:
        error_msg = f"❌ Error: {e}\n\nMake sure:\n1. Vector store is loaded\n2. Ollama Desktop is running\n3. Model llama3.1 is available"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return history

def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(title="DevOps RAG Chat") as demo:
        gr.Markdown("""
        # 🤖 DevOps Knowledgebase - RAG Chat Interface
        
        Ask questions about your DevOps documentation. The system will search through your indexed PDFs and provide answers using Ollama.
        
        **Status:** ✅ System Ready | 📊 Type `stats` for system info | 💡 Type `help` for commands
        """)
        
        chatbot = gr.Chatbot(
            label="Chat History",
            height=500
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Your Question",
                placeholder="Ask anything about your DevOps documentation...",
                lines=2,
                scale=4
            )
            submit = gr.Button("Send", variant="primary", scale=1)
        
        with gr.Row():
            clear = gr.Button("Clear Chat")
        
        gr.Markdown("""
        ---
        **Quick Tips:**
        - Be specific in your questions for better results
        - The system searches your 3,992 document chunks (top 3 matches used)
        - Responses are optimized for speed while maintaining quality
        - Sources are shown with each answer
        - First response may take 5-10 seconds while the model loads
        """)
        
        # Event handlers
        msg.submit(chat_with_rag, [msg, chatbot], [chatbot])
        msg.submit(lambda: "", None, [msg])  # Clear input after submit
        
        submit.click(chat_with_rag, [msg, chatbot], [chatbot])
        submit.click(lambda: "", None, [msg])  # Clear input after submit
        
        clear.click(lambda: [], None, [chatbot])
    
    return demo

if __name__ == "__main__":
    print("=" * 70)
    print("  DevOps Knowledgebase - Web Chat Interface")
    print("=" * 70)
    
    # Initialize
    success = initialize_rag()
    
    if not success:
        print("\n❌ Failed to initialize RAG system")
        print("Please make sure:")
        print("  1. Vector store exists (run: python index_pdfs.py)")
        print("  2. Ollama Desktop is running")
        print("  3. Required packages installed (pip install gradio)")
        sys.exit(1)
    
    print("\n✅ RAG system initialized successfully!")
    print("\n🚀 Starting web interface...")
    print("=" * 70)
    
    # Create and launch interface
    demo = create_interface()
    
    # Launch with share=False for local use only
    demo.launch(
        server_name="127.0.0.1",  # Local only
        server_port=None,          # Auto-select available port
        share=False,               # Don't create public link
        inbrowser=True             # Auto-open in browser
    )
