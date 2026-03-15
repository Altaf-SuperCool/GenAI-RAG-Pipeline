"""
Simple Notebook Runner - Run pdf_loader.ipynb easily
This is the simplified version for quick execution
"""

import os
import sys

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           PDF Loader Notebook - Simple Runner                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# Check if we're in the right directory
if not os.path.exists('notebooks/pdf_loader.ipynb'):
    print("❌ Error: notebooks/pdf_loader.ipynb not found")
    print("\n💡 Please run this script from the project root directory")
    sys.exit(1)

print("\n📋 Checking dependencies...")

# Check for required packages
try:
    import papermill
    method = 'papermill'
    print("✅ papermill available (recommended)")
except ImportError:
    print("⚠️  papermill not found, will try nbconvert")
    method = 'nbconvert'

print(f"\n🚀 Running notebook with {method}...")
print("="*70)

if method == 'papermill':
    # Use papermill (best for automation)
    try:
        import papermill as pm
        
        pm.execute_notebook(
            'notebooks/pdf_loader.ipynb',
            'notebooks/pdf_loader_executed.ipynb',
            kernel_name='python3',
            progress_bar=True
        )
        
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print("\nNotebook executed successfully!")
        print("Results saved to: notebooks/pdf_loader_executed.ipynb")
        print("\nYour vector store has been updated with embeddings!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install papermill: pip install papermill")
        print("2. Or use interactive mode: jupyter notebook notebooks/pdf_loader.ipynb")
        sys.exit(1)

else:
    # Use nbconvert
    import subprocess
    
    try:
        result = subprocess.run([
            'jupyter', 'nbconvert',
            '--to', 'notebook',
            '--execute',
            'notebooks/pdf_loader.ipynb',
            '--output', 'pdf_loader_executed.ipynb'
        ], capture_output=True, text=True, check=True)
        
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print("\nNotebook executed successfully!")
        print("Results saved to: notebooks/pdf_loader_executed.ipynb")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e.stderr}")
        print("\nTroubleshooting:")
        print("1. Install papermill for better execution: pip install papermill")
        print("2. Or open manually: jupyter notebook notebooks/pdf_loader.ipynb")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: jupyter command not found")
        print("\nInstall Jupyter:")
        print("  pip install jupyter")
        sys.exit(1)

print("\n📊 Quick Stats:")
try:
    from src.vector_store_factory import get_vector_store
    store = get_vector_store(dimension=384)
    store.load()
    stats = store.get_stats()
    print(f"  Total Vectors: {stats['total_vectors']}")
    print(f"  Vector DB Type: {stats['type']}")
except:
    print("  (Run test_ollama_connection.py to see stats)")

print("\n🎯 Next Steps:")
print("  1. Test your RAG: python tests/quick_test.py")
print("  2. Interactive chat: python tests/test_rag_chat.py")
print("  3. Test connection: python tests/test_ollama_connection.py")
