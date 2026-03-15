"""
Fast-Loading Web Chat Interface for RAG System
Optimized for quick startup with lazy loading
"""
import os
import sys
import gradio as gr
from typing import Optional
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Global variables for lazy loading
vector_store = None
embedding_manager = None
llm = None
initialization_status = {"loaded": False, "error": None}

def lazy_load_components():
    """Load components only when needed"""
    global vector_store, embedding_manager, llm, initialization_status
    
    if initialization_status["loaded"]:
        return True
    
    if initialization_status["error"]:
        return False
    
    try:
        print("⏳ Loading RAG components...")
        start_time = time.time()
        
        # Load vector store (fast)
        from src.vector_store_factory import get_vector_store
        vector_store = get_vector_store()
        vector_store.load()
        print(f"   ✅ Vector store loaded ({time.time() - start_time:.1f}s)")
        
        # Load embedding model (slower)
        from src.embedding import EmbeddingManager
        embedding_manager = EmbeddingManager()
        print(f"   ✅ Embeddings ready ({time.time() - start_time:.1f}s)")
        
        # Connect to Ollama (can be slow)
        try:
            from langchain_ollama import ChatOllama
            llm = ChatOllama(
                model="llama3.1",
                temperature=0.7,
                base_url="http://localhost:11434"
            )
            print(f"   ✅ Ollama connected ({time.time() - start_time:.1f}s)")
        except Exception as e:
            print(f"   ⚠️ Ollama connection delayed: {e}")
            llm = None
        
        initialization_status["loaded"] = True
        print(f"✅ Total load time: {time.time() - start_time:.1f}s")
        return True
        
    except Exception as e:
        print(f"❌ Error loading: {e}")
        initialization_status["error"] = str(e)
        return False

def chat_response(message, history):
    """Handle chat messages with lazy loading"""
    if not message.strip():
        return history
    
    # Load components on first message
    if not initialization_status["loaded"]:
        yield history + [[message, "⏳ Loading RAG system... (this takes ~10-20 seconds on first use)"]]
        
        if not lazy_load_components():
            error_msg = f"❌ Failed to load RAG system: {initialization_status['error']}\n\n"
            error_msg += "**Troubleshooting:**\n"
            error_msg += "1. Make sure Ollama Desktop is running\n"
            error_msg += "2. Run: `python index_pdfs.py` if vectors not found\n"
            error_msg += "3. Check: `ollama list` shows llama3.1"
            yield history + [[message, error_msg]]
            return
        
        yield history + [[message, "✅ System loaded! Processing your question..."]]
    
    # Handle special commands
    if message.lower() == "stats":
        stats = f"""📊 **System Statistics**

- **Vectors:** {vector_store.total_vectors:,}
- **Embedding Dim:** {embedding_manager.dimension}
- **Vector DB:** FAISS
- **LLM:** llama3.1 (Ollama)
- **Status:** {'🟢 Online' if llm else '🟡 Offline'}

Type any question to search your documents!"""
        yield history + [[message, stats]]
        return
    
    if message.lower() in ["help", "commands"]:
        help_text = """💡 **How to Use**

**Just type your question!** Examples:
- "What is the platform architecture?"
- "Tell me about DevOps tools"
- "Explain the deployment process"

**Special Commands:**
- `stats` - Show system info
- `help` - Show this message

The system searches through your 3,992 document chunks and provides answers with sources."""
        yield history + [[message, help_text]]
        return
    
    # Search documents
    try:
        # Show searching status
        yield history + [[message, "🔍 Searching documents..."]]
        
        query_embedding = embedding_manager.embed_query(message)
        results = vector_store.search(query_embedding, top_k=5)
        
        if not results:
            yield history + [[message, "❌ No relevant documents found. Try rephrasing your question."]]
            return
        
        # Show generating status
        yield history + [[message, "🤖 Generating answer..."]]
        
        # Build context
        context = "\n\n".join([
            f"[Source: {r['metadata'].get('source', 'Unknown')}]\n{r['metadata'].get('text', r['metadata'].get('content', ''))[:500]}"
            for r in results[:3]
        ])
        
        prompt = f"""Answer this question based on the provided context from documentation.

Context:
{context}

Question: {message}

Provide a clear, concise answer. If the context doesn't fully answer the question, say what you can determine from it."""
        
        if llm:
            try:
                response = llm.invoke(prompt)
                answer = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                answer = f"⚠️ Ollama error: {e}\n\nTry restarting Ollama Desktop app."
        else:
            answer = "⚠️ Ollama not connected. Make sure Ollama Desktop is running."
        
        # Format sources
        sources = "\n\n---\n\n📚 **Sources:**\n\n"
        for i, r in enumerate(results[:3], 1):
            source = r['metadata'].get('source', 'Unknown').split('\\')[-1].split('/')[-1]
            conf = max(0, 100 - (r.get('distance', 0) * 100))
            preview = r['metadata'].get('text', r['metadata'].get('content', ''))[:150]
            sources += f"{i}. **{source}** ({conf:.0f}% match)\n   _{preview}..._\n\n"
        
        final_response = answer + sources
        yield history + [[message, final_response]]
        
    except Exception as e:
        error_response = f"❌ Error: {e}\n\nMake sure Ollama Desktop is running and try again."
        yield history + [[message, error_response]]

# Create interface
with gr.Blocks(title="DevOps RAG Chat") as demo:
    gr.Markdown("""
    # 🤖 DevOps Knowledgebase - RAG Chat
    
    Ask questions about your DevOps documentation!
    
    **Status:** Type your first question to load the system | 📊 Type `stats` for info | 💡 Type `help` for commands
    """)
    
    chatbot = gr.Chatbot(
        label="Chat",
        height=500
    )
    
    msg = gr.Textbox(
        label="Your Question",
        placeholder="Ask anything about your DevOps documentation...",
        lines=2
    )
    
    with gr.Row():
        submit = gr.Button("Send", variant="primary")
        clear = gr.Button("Clear")
    
    gr.Markdown("""
    **💡 Tips:**
    - First message loads the system (~10-20 seconds)
    - Subsequent messages are fast
    - Searches 3,992 document chunks from your PDFs
    - Shows sources with each answer
    """)
    
    # Event handlers
    submit.click(chat_response, [msg, chatbot], [chatbot])
    submit.click(lambda: "", None, [msg])
    
    msg.submit(chat_response, [msg, chatbot], [chatbot])
    msg.submit(lambda: "", None, [msg])
    
    clear.click(lambda: [], None, [chatbot])

if __name__ == "__main__":
    print("=" * 70)
    print("  DevOps RAG - Fast Web Chat (Lazy Loading)")
    print("=" * 70)
    print("\n✅ Starting web server...")
    print("📝 Components will load on first message")
    print("🚀 Opening browser at http://127.0.0.1:7860")
    print("\n💡 First message takes 10-20 seconds (loading models)")
    print("   Subsequent messages are much faster!\n")
    print("=" * 70)
    
    # Launch with minimal startup time
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_api=False
    )
