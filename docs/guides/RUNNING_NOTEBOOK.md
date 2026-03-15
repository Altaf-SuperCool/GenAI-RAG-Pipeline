# Running pdf_loader.ipynb Programmatically

## 🎯 Three Ways to Run Your Notebook

You have multiple options to run the `pdf_loader.ipynb` notebook programmatically for automation or batch processing.

---

## ⚡ Method 1: Simple Script (Recommended)

### Quick Start

```powershell
cd "C:\Users\v193570\Documents\Agentic AI\Agentic_RAG"
python run_notebook_simple.py
```

This will:
- ✅ Execute all cells in the notebook
- ✅ Generate/update embeddings
- ✅ Save results to a new notebook
- ✅ Show you the statistics

**Best for**: Quick execution, automation, scheduled runs

---

## 🔧 Method 2: Advanced Script with Options

### Installation

First, install papermill for better notebook execution:

```powershell
pip install papermill
```

### Usage

```powershell
# Basic execution (recommended)
python run_notebook.py --method papermill

# Execute and save as HTML
python run_notebook.py --method nbconvert --format html

# Extract and run code (for debugging)
python run_notebook.py --method extract

# Open in Jupyter browser
python run_notebook.py --method interactive
```

### Options

| Method | Description | Best For |
|--------|-------------|----------|
| `papermill` | Execute with progress tracking | Automation, CI/CD |
| `nbconvert` | Convert and execute | Exporting to HTML/PDF |
| `extract` | Run code step-by-step | Debugging |
| `interactive` | Open in browser | Manual execution |

### Examples

```powershell
# Run with papermill (best for automation)
python run_notebook.py --method papermill

# Export to HTML after execution
python run_notebook.py --method nbconvert --format html

# Open in Jupyter
python run_notebook.py --method interactive

# Custom output path
python run_notebook.py --method papermill --output results/my_output.ipynb
```

---

## 📓 Method 3: Direct Jupyter Commands

### Execute Without Opening Browser

```powershell
# Using nbconvert
jupyter nbconvert --to notebook --execute notebook/pdf_loader.ipynb --output pdf_loader_executed.ipynb

# Or using papermill
papermill notebook/pdf_loader.ipynb notebook/pdf_loader_executed.ipynb
```

### Open in Jupyter Browser

```powershell
jupyter notebook notebook/pdf_loader.ipynb
```

Then manually click "Run All" in the browser.

---

## 🔄 Method 4: Python API (For Integration)

If you want to integrate notebook execution into your own Python code:

```python
import papermill as pm

# Execute notebook
pm.execute_notebook(
    'notebook/pdf_loader.ipynb',
    'notebook/pdf_loader_executed.ipynb',
    parameters={},  # Can pass parameters if notebook supports them
    kernel_name='python3'
)

print("Notebook executed!")
```

Or with nbconvert:

```python
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

# Read notebook
with open('notebook/pdf_loader.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

# Execute
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
ep.preprocess(nb)

# Save
with open('notebook/pdf_loader_executed.ipynb', 'w') as f:
    nbformat.write(nb, f)

print("Notebook executed!")
```

---

## 📊 Comparison of Methods

| Method | Pros | Cons | Use When |
|--------|------|------|----------|
| **Simple Script** | ✅ One command<br>✅ No options to worry about | ⚠️ Less flexible | Quick execution |
| **Advanced Script** | ✅ Many options<br>✅ Multiple formats | ⚠️ More complex | Need flexibility |
| **Direct Jupyter** | ✅ Standard tools<br>✅ Well documented | ⚠️ Manual commands | CI/CD pipelines |
| **Python API** | ✅ Full control<br>✅ Integration | ⚠️ Need to write code | Custom workflows |

---

## 🛠️ Setup Requirements

### Install Required Packages

```powershell
# For simple execution
pip install jupyter nbconvert

# For better execution (recommended)
pip install papermill jupyter nbconvert

# Or install all requirements
pip install -r requirements.txt
```

### Verify Installation

```powershell
# Check jupyter
jupyter --version

# Check papermill (if installed)
papermill --version

# Check python
python --version
```

---

## 🎯 Common Use Cases

### Use Case 1: Daily Automated Execution

Create a batch file `run_daily.bat`:

```batch
@echo off
cd "C:\Users\v193570\Documents\Agentic AI\Agentic_RAG"
python run_notebook_simple.py
pause
```

Schedule this in Windows Task Scheduler to run daily.

### Use Case 2: CI/CD Pipeline

In your CI/CD script:

```yaml
# GitHub Actions example
- name: Execute Notebook
  run: |
    pip install papermill
    python run_notebook.py --method papermill
```

### Use Case 3: Process New PDFs

```python
# Custom script
import os
import papermill as pm

# Add new PDFs to data/pdf/
new_pdfs = ['doc1.pdf', 'doc2.pdf']
for pdf in new_pdfs:
    # Copy to data/pdf/
    # Then run notebook
    pm.execute_notebook(
        'notebook/pdf_loader.ipynb',
        f'results/processed_{pdf}.ipynb'
    )
```

### Use Case 4: Export Results to HTML

```powershell
# Generate HTML report
python run_notebook.py --method nbconvert --format html
```

Opens `pdf_loader.html` with all outputs.

---

## 🐛 Troubleshooting

### Issue: "papermill not found"

**Solution:**
```powershell
pip install papermill
```

### Issue: "jupyter command not found"

**Solution:**
```powershell
pip install jupyter
```

### Issue: "Kernel error" or "No module named..."

**Solution:**
```powershell
# Reinstall requirements
pip install -r requirements.txt

# Or install specific package
pip install sentence-transformers langchain-ollama
```

### Issue: Notebook execution hangs

**Solution:**
- Check if cells have infinite loops
- Increase timeout: `pm.execute_notebook(..., timeout=1800)`  # 30 minutes
- Run interactively to find problem cell

### Issue: "FileNotFoundError: notebook/pdf_loader.ipynb"

**Solution:**
```powershell
# Make sure you're in the right directory
cd "C:\Users\v193570\Documents\Agentic AI\Agentic_RAG"

# Then run
python run_notebook_simple.py
```

---

## ⚙️ Advanced Configuration

### Custom Parameters

If you modify your notebook to accept parameters, you can pass them:

```python
import papermill as pm

pm.execute_notebook(
    'notebook/pdf_loader.ipynb',
    'output.ipynb',
    parameters={
        'pdf_directory': 'custom_pdfs/',
        'chunk_size': 1500,
        'top_k': 10
    }
)
```

### Progress Tracking

```python
import papermill as pm

pm.execute_notebook(
    'notebook/pdf_loader.ipynb',
    'output.ipynb',
    progress_bar=True,  # Show progress
    log_output=True     # Print output
)
```

### Error Handling

```python
import papermill as pm

try:
    pm.execute_notebook(
        'notebook/pdf_loader.ipynb',
        'output.ipynb',
        kernel_name='python3'
    )
    print("✅ Success!")
except pm.PapermillExecutionError as e:
    print(f"❌ Execution failed at cell: {e}")
    # Handle error
```

---

## 📋 Quick Reference

### Simple Execution
```powershell
python run_notebook_simple.py
```

### With Options
```powershell
python run_notebook.py --method papermill
python run_notebook.py --method nbconvert --format html
python run_notebook.py --method interactive
```

### Direct Commands
```powershell
papermill notebook/pdf_loader.ipynb output.ipynb
jupyter nbconvert --execute --to notebook notebook/pdf_loader.ipynb
jupyter notebook notebook/pdf_loader.ipynb
```

---

## 🎉 After Execution

Once the notebook runs successfully:

1. **Check Results**
   ```powershell
   python test_ollama_connection.py
   ```

2. **Test RAG System**
   ```powershell
   python quick_test.py
   ```

3. **Start Interactive Chat**
   ```powershell
   python test_rag_chat.py
   ```

---

## 💡 Tips

1. **First Time**: Use `python run_notebook_simple.py` - it's the easiest
2. **Automation**: Use `papermill` method for scripts and CI/CD
3. **Debugging**: Use `--method extract` to run cells one-by-one
4. **Reports**: Use `--format html` to create shareable reports
5. **Regular Updates**: Schedule daily runs to keep embeddings fresh

---

## 📞 Need Help?

If execution fails:

1. Check requirements: `pip install -r requirements.txt`
2. Test Ollama: `ollama list`
3. Verify PDFs: Check `data/pdf/` has PDF files
4. Run diagnostics: `python test_ollama_connection.py`

For detailed debugging, use:
```powershell
python run_notebook.py --method extract
```

This will show exactly which cell fails.

---

**Quick Start Summary:**

```powershell
# Navigate to project
cd "C:\Users\v193570\Documents\Agentic AI\Agentic_RAG"

# Install dependencies
pip install papermill

# Run notebook
python run_notebook_simple.py

# Test results
python quick_test.py
```

That's it! 🚀
