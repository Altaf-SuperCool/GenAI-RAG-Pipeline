"""
Simple PDF Indexing Script
Uses the factory-based vector store architecture to index PDFs
"""
import os
import sys
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.vector_store_factory import get_vector_store, get_vector_store_info


class SimpleEmbeddingManager:
    """Simple wrapper for embedding generation"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"   Loaded: {model_name}")
    
    def generate_embeddings(self, texts):
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings


def load_pdfs_from_directory(pdf_dir: str):
    """Load all PDFs from a directory"""
    pdf_dir = Path(pdf_dir)
    if not pdf_dir.exists():
        print(f"❌ Error: Directory not found: {pdf_dir}")
        return []
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"⚠️  No PDF files found in {pdf_dir}")
        return []
    
    print(f"📄 Found {len(pdf_files)} PDF files")
    
    all_documents = []
    for pdf_file in pdf_files:
        try:
            print(f"   Loading: {pdf_file.name}...", end=" ")
            loader = PyMuPDFLoader(str(pdf_file))
            docs = loader.load()
            all_documents.extend(docs)
            print(f"✅ {len(docs)} pages")
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    return all_documents


def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into chunks"""
    print(f"\n📝 Splitting {len(documents)} pages into chunks...")
    print(f"   Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks")
    
    return chunks


def index_documents(chunks):
    """Generate embeddings and index documents"""
    print(f"\n🔧 Initializing components...")
    
    # Show which vector store is being used
    db_info = get_vector_store_info()
    print(f"   Vector DB: {db_info['type']}")
    if db_info['type'] == 'milvus':
        print(f"   Milvus Host: {db_info['config']['host']}:{db_info['config']['port']}")
    
    # Initialize embedding manager
    print(f"\n🧮 Loading embedding model...")
    embedding_manager = SimpleEmbeddingManager()
    print(f"   Dimension: {embedding_manager.dimension}")
    
    # Initialize vector store
    print(f"\n💾 Initializing vector store...")
    vector_store = get_vector_store()
    vector_store.initialize()
    
    # Extract text from chunks
    print(f"\n📝 Extracting text from chunks...")
    texts = [chunk.page_content for chunk in chunks]
    
    # Generate embeddings (in batches to avoid memory issues)
    print(f"\n🎯 Generating embeddings...")
    batch_size = 100
    total_indexed = 0
    
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_texts = texts[i:i + batch_size]
        
        # Generate embeddings for batch
        embeddings = embedding_manager.generate_embeddings(batch_texts)
        
        # Prepare metadata
        metadata = []
        for chunk in batch_chunks:
            meta = chunk.metadata.copy()
            meta['content'] = chunk.page_content
            meta['content_length'] = len(chunk.page_content)
            metadata.append(meta)
        
        # Add to vector store
        vector_store.add_embeddings(embeddings, metadata)
        
        total_indexed += len(batch_chunks)
        print(f"   Progress: {total_indexed}/{len(chunks)} chunks indexed")
    
    # Save vector store
    print(f"\n💾 Saving vector store...")
    vector_store.save()
    
    # Get stats
    stats = vector_store.get_stats()
    print(f"\n✅ Indexing Complete!")
    print(f"   Total vectors: {stats['total_vectors']}")
    
    return vector_store


def main():
    """Main indexing pipeline"""
    print("=" * 70)
    print("  PDF INDEXING SCRIPT - DevOps Knowledgebase RAG Pipeline")
    print("=" * 70)
    
    # Configuration
    pdf_directory = "data/pdf"
    chunk_size = 1000
    chunk_overlap = 200
    
    # Step 1: Load PDFs
    print(f"\n📋 Step 1: Loading PDFs from {pdf_directory}")
    print("-" * 70)
    documents = load_pdfs_from_directory(pdf_directory)
    
    if not documents:
        print("\n❌ No documents to index. Exiting.")
        return
    
    print(f"\n✅ Loaded {len(documents)} pages total")
    
    # Step 2: Split into chunks
    print(f"\n📋 Step 2: Splitting documents into chunks")
    print("-" * 70)
    chunks = split_documents(documents, chunk_size, chunk_overlap)
    
    # Step 3: Index documents
    print(f"\n📋 Step 3: Generating embeddings and indexing")
    print("-" * 70)
    try:
        vector_store = index_documents(chunks)
        
        print("\n" + "=" * 70)
        print("  INDEXING SUCCESSFUL!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   • PDF files processed: {len(set(doc.metadata.get('source', 'unknown') for doc in documents))}")
        print(f"   • Total pages: {len(documents)}")
        print(f"   • Total chunks: {len(chunks)}")
        print(f"   • Vectors indexed: {vector_store.total_vectors}")
        print(f"\n🎉 Your RAG system is ready to use!")
        print(f"\n💡 Next steps:")
        print(f"   1. Test the connection: python tests/test_ollama_connection.py")
        print(f"   2. Try a quick query: python tests/quick_test.py")
        print(f"   3. Start chatting: python tests/test_rag_chat.py")
        
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
