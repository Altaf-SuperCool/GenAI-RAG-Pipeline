"""
Run pdf_loader.ipynb Notebook Programmatically
This script executes the Jupyter notebook and can be used for automation
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_with_papermill(notebook_path, output_path=None, parameters=None):
    """
    Run notebook using papermill (recommended for automation)
    
    Install: pip install papermill
    """
    try:
        import papermill as pm
        
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '_executed.ipynb')
        
        print(f"🚀 Running notebook with papermill...")
        print(f"   Input: {notebook_path}")
        print(f"   Output: {output_path}")
        
        pm.execute_notebook(
            notebook_path,
            output_path,
            parameters=parameters or {},
            kernel_name='python3'
        )
        
        print("✅ Notebook executed successfully!")
        print(f"   Results saved to: {output_path}")
        return True
        
    except ImportError:
        print("❌ papermill not installed")
        print("   Install with: pip install papermill")
        return False
    except Exception as e:
        print(f"❌ Error executing notebook: {e}")
        return False


def run_with_nbconvert(notebook_path, output_format='notebook'):
    """
    Run notebook using nbconvert
    
    Args:
        output_format: 'notebook', 'html', 'pdf', 'python'
    """
    try:
        print(f"🚀 Running notebook with nbconvert...")
        print(f"   Input: {notebook_path}")
        print(f"   Format: {output_format}")
        
        # Execute and save
        cmd = [
            'jupyter', 'nbconvert',
            '--to', output_format,
            '--execute',
            notebook_path
        ]
        
        if output_format == 'notebook':
            output_path = notebook_path.replace('.ipynb', '_executed.ipynb')
            cmd.extend(['--output', output_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Notebook executed successfully!")
            if output_format == 'notebook':
                print(f"   Results saved to: {output_path}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing notebook: {e}")
        return False


def run_interactive(notebook_path):
    """
    Open notebook in Jupyter for interactive execution
    """
    try:
        print(f"🚀 Opening notebook in Jupyter...")
        print(f"   Path: {notebook_path}")
        
        # Open in Jupyter
        subprocess.Popen(['jupyter', 'notebook', notebook_path])
        
        print("✅ Jupyter opened!")
        print("   Execute cells manually in the browser")
        return True
        
    except Exception as e:
        print(f"❌ Error opening Jupyter: {e}")
        return False


def run_specific_cells(notebook_path, cell_tags=None):
    """
    Run only specific tagged cells
    
    Requires papermill and cell tags in notebook
    """
    try:
        import papermill as pm
        
        print(f"🚀 Running specific cells...")
        print(f"   Tags: {cell_tags}")
        
        # This requires cells to be tagged in the notebook
        # For now, run all cells
        return run_with_papermill(notebook_path)
        
    except ImportError:
        print("❌ papermill not installed")
        return False


def extract_and_run_code(notebook_path):
    """
    Extract Python code from notebook and run it
    """
    try:
        import nbformat
        
        print(f"🚀 Extracting and running code from notebook...")
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Extract code cells
        code_cells = [cell['source'] for cell in nb.cells if cell['cell_type'] == 'code']
        
        print(f"   Found {len(code_cells)} code cells")
        
        # Execute code
        for i, code in enumerate(code_cells, 1):
            print(f"\n{'='*70}")
            print(f"Executing Cell {i}/{len(code_cells)}")
            print('='*70)
            
            try:
                exec(code, globals())
                print(f"✅ Cell {i} executed")
            except Exception as e:
                print(f"❌ Error in cell {i}: {e}")
                
                # Ask if should continue
                response = input("\nContinue to next cell? (y/n): ")
                if response.lower() != 'y':
                    return False
        
        print("\n✅ All cells executed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Run pdf_loader.ipynb notebook programmatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with papermill (recommended for automation)
  python run_notebook.py --method papermill
  
  # Run with nbconvert
  python run_notebook.py --method nbconvert
  
  # Open in Jupyter browser
  python run_notebook.py --method interactive
  
  # Extract and run code
  python run_notebook.py --method extract
  
  # Export to HTML
  python run_notebook.py --method nbconvert --format html
        """
    )
    
    parser.add_argument(
        '--notebook',
        default='notebooks/pdf_loader.ipynb',
        help='Path to notebook (default: notebooks/pdf_loader.ipynb)'
    )
    
    parser.add_argument(
        '--method',
        choices=['papermill', 'nbconvert', 'interactive', 'extract'],
        default='papermill',
        help='Execution method (default: papermill)'
    )
    
    parser.add_argument(
        '--format',
        choices=['notebook', 'html', 'pdf', 'python'],
        default='notebook',
        help='Output format for nbconvert (default: notebook)'
    )
    
    parser.add_argument(
        '--output',
        help='Output path (optional)'
    )
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           PDF Loader Notebook Execution Script                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if notebook exists
    notebook_path = args.notebook
    if not os.path.exists(notebook_path):
        print(f"❌ Notebook not found: {notebook_path}")
        print("\n💡 Make sure you're in the Agentic_RAG directory")
        sys.exit(1)
    
    print(f"📓 Notebook: {notebook_path}")
    print(f"🔧 Method: {args.method}")
    print("="*70)
    
    # Execute based on method
    success = False
    
    if args.method == 'papermill':
        success = run_with_papermill(notebook_path, args.output)
        
    elif args.method == 'nbconvert':
        success = run_with_nbconvert(notebook_path, args.format)
        
    elif args.method == 'interactive':
        success = run_interactive(notebook_path)
        
    elif args.method == 'extract':
        success = extract_and_run_code(notebook_path)
    
    if success:
        print("\n" + "="*70)
        print("🎉 SUCCESS!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ FAILED")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
