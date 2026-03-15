# Vector Database Configuration Guide

## Overview

The DevOps Knowledgebase RAG system now supports **multiple vector database backends** with a flexible factory pattern. You can easily switch between **FAISS** (local, fast) and **Milvus** (enterprise, scalable) by simply changing an environment variable.

## Supported Vector Databases

### 1. FAISS (Default)
- **Type**: Library-based, in-memory with disk persistence
- **Best for**: Development, prototypes, < 1M vectors
- **Pros**: 
  - ✅ Zero infrastructure - just a library
  - ✅ Fast for small-medium datasets
  - ✅ No server required
  - ✅ Free and open-source
- **Cons**:
  - ⚠️ Limited scalability (> 1M vectors)
  - ⚠️ No built-in filtering
  - ⚠️ Updates/deletes are difficult
- **Use when**: Quick start, development, single-user, < 1M vectors

### 2. Milvus (Enterprise Option)
- **Type**: Distributed vector database server
- **Best for**: Production, enterprise, > 1M vectors
- **Pros**:
  - ✅ Scales to billions of vectors
  - ✅ Advanced filtering and hybrid search
  - ✅ Multi-tenancy support
  - ✅ ACID transactions
  - ✅ Real-time updates/deletes
  - ✅ Monitoring and metrics
- **Cons**:
  - ⚠️ Requires server infrastructure
  - ⚠️ More complex setup
  - ⚠️ Higher resource requirements
- **Use when**: Production deployment, large datasets, multi-user

## Quick Start

### Using FAISS (Default - No Setup Required)

1. **Set environment variable** in `.env`:
```bash
VECTOR_DB_TYPE=faiss
```

2. **Use in code**:
```python
from src.vector_store_factory import get_vector_store

# Create store (automatically uses FAISS)
store = get_vector_store(dimension=384)

# Add embeddings
store.add_embeddings(embeddings, metadata)

# Search
results = store.search(query_vector, top_k=5)

# Save
store.save()
```

✅ That's it! No server setup needed.

### Using Milvus (Requires Server)

#### Step 1: Start Milvus Server

**Option A: Docker Compose (Recommended)**
```bash
# Download docker-compose file
curl -O https://github.com/milvus-io/milvus/releases/download/v2.3.3/milvus-standalone-docker-compose.yml

# Rename for convenience
mv milvus-standalone-docker-compose.yml docker-compose-milvus.yml

# Start Milvus
docker-compose -f docker-compose-milvus.yml up -d

# Verify
docker ps | grep milvus
```

**Option B: Manual Installation**
```bash
# See: https://milvus.io/docs/install_standalone-docker.md
```

#### Step 2: Install Python Client
```bash
pip install pymilvus
```

Or uncomment in `requirements.txt`:
```txt
pymilvus             # Enterprise distributed vector DB (optional)
```

Then run:
```bash
pip install -r requirements.txt
```

#### Step 3: Configure Environment

Update `.env` file:
```bash
# Vector Database Configuration
VECTOR_DB_TYPE=milvus

# Milvus Connection Settings
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=devops_knowledgebase
```

#### Step 4: Use in Code

```python
from src.vector_store_factory import get_vector_store

# Create store (automatically uses Milvus)
store = get_vector_store(dimension=384)

# Same interface as FAISS!
store.add_embeddings(embeddings, metadata)
results = store.search(query_vector, top_k=5)
store.save()
```

## Configuration Reference

### Environment Variables

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `VECTOR_DB_TYPE` | `faiss`, `milvus` | `faiss` | Which vector DB to use |
| `MILVUS_HOST` | hostname/IP | `localhost` | Milvus server host |
| `MILVUS_PORT` | port number | `19530` | Milvus server port |
| `MILVUS_COLLECTION_NAME` | string | `devops_knowledgebase` | Collection/table name |

### Example `.env` File

```bash
# ===== Vector Database Configuration =====
# Options: 'faiss' or 'milvus'
VECTOR_DB_TYPE=faiss

# Milvus settings (only needed if VECTOR_DB_TYPE=milvus)
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=devops_knowledgebase
```

## Usage Examples

### Example 1: Default Configuration (from .env)

```python
from src.vector_store_factory import get_vector_store

# Reads VECTOR_DB_TYPE from .env
store = get_vector_store(dimension=384)
```

### Example 2: Force Specific Type

```python
# Always use FAISS regardless of .env
store = get_vector_store(store_type='faiss', dimension=384)

# Always use Milvus regardless of .env
store = get_vector_store(store_type='milvus', dimension=384)
```

### Example 3: Custom Configuration

```python
# FAISS with custom directory
store = get_vector_store(
    store_type='faiss',
    dimension=384,
    persist_dir='my_custom_data/vectors'
)

# Milvus with custom server
store = get_vector_store(
    store_type='milvus',
    dimension=384,
    host='milvus.mycompany.com',
    port=19530,
    collection_name='my_docs'
)
```

### Example 4: Check Configuration

```python
from src.vector_store_factory import get_vector_store_info

# See what will be used
info = get_vector_store_info()
print(f"Type: {info['type']}")
print(f"Config: {info['config']}")
```

## Common Patterns

### Pattern 1: Development with FAISS, Production with Milvus

```python
import os
from src.vector_store_factory import get_vector_store

# Use environment to control
# Development: VECTOR_DB_TYPE=faiss
# Production: VECTOR_DB_TYPE=milvus
store = get_vector_store(dimension=384)
```

### Pattern 2: Graceful Fallback

```python
from src.vector_store_factory import get_vector_store

try:
    # Try Milvus first
    store = get_vector_store(store_type='milvus', dimension=384)
except Exception as e:
    print(f"Milvus unavailable, falling back to FAISS: {e}")
    store = get_vector_store(store_type='faiss', dimension=384)
```

### Pattern 3: Migration from FAISS to Milvus

```python
from src.vector_store_factory import get_vector_store
import numpy as np

# Load existing FAISS data
faiss_store = get_vector_store(store_type='faiss', dimension=384)
faiss_store.load()

# Create new Milvus store
milvus_store = get_vector_store(store_type='milvus', dimension=384)

# Get all FAISS data
# Note: You'll need to implement export/import for large-scale migration
# For now, re-process documents with Milvus store

print(f"Ready to migrate {faiss_store.total_vectors} vectors")
```

## Testing Your Setup

### Test FAISS

```python
from src.vector_store_factory import get_vector_store
import numpy as np

# Create store
store = get_vector_store(store_type='faiss', dimension=384)

# Test data
embeddings = np.random.rand(10, 384).astype('float32')
metadata = [{'text': f'Test doc {i}', 'source': 'test.pdf', 'page_number': i} for i in range(10)]

# Add
store.add_embeddings(embeddings, metadata)

# Search
query = np.random.rand(384).astype('float32')
results = store.search(query, top_k=3)

print(f"✅ FAISS working! Found {len(results)} results")
print(f"Stats: {store.get_stats()}")
```

### Test Milvus

```python
from src.vector_store_factory import get_vector_store
import numpy as np

try:
    # Create store
    store = get_vector_store(store_type='milvus', dimension=384)
    
    # Test data
    embeddings = np.random.rand(10, 384).astype('float32')
    metadata = [
        {
            'text': f'Test doc {i}',
            'source': 'test.pdf',
            'page_number': i,
            'chunk_index': i
        }
        for i in range(10)
    ]
    
    # Add
    store.add_embeddings(embeddings, metadata)
    
    # Search
    query = np.random.rand(384).astype('float32')
    results = store.search(query, top_k=3)
    
    print(f"✅ Milvus working! Found {len(results)} results")
    print(f"Stats: {store.get_stats()}")
    
    # Cleanup
    store.delete_all()
    store.disconnect()
    
except Exception as e:
    print(f"❌ Milvus test failed: {e}")
    print("Make sure Milvus server is running: docker-compose up -d")
```

## Troubleshooting

### FAISS Issues

**Problem**: `FileNotFoundError: Index file not found`
- **Solution**: Index not created yet. Run document ingestion first.

**Problem**: `RuntimeError: Error in void faiss::read_index`
- **Solution**: Corrupted index file. Delete and rebuild.

### Milvus Issues

**Problem**: `ConnectionError: Failed to connect to Milvus`
- **Solution**: 
  1. Check if Milvus is running: `docker ps | grep milvus`
  2. Start Milvus: `docker-compose up -d`
  3. Check host/port in `.env`

**Problem**: `ImportError: No module named 'pymilvus'`
- **Solution**: Install pymilvus: `pip install pymilvus`

**Problem**: Collection already exists with different schema
- **Solution**: Delete collection and recreate:
  ```python
  store.delete_all()  # Then reinitialize
  ```

## Performance Comparison

### FAISS vs Milvus

| Metric | FAISS | Milvus |
|--------|-------|--------|
| **Setup Time** | Instant | 5-10 min (Docker) |
| **Search Speed (10K vectors)** | 0.1-0.3s | 0.1-0.4s |
| **Search Speed (1M vectors)** | 0.5-1s | 0.2-0.5s |
| **Search Speed (10M vectors)** | 5-10s | 0.3-0.8s |
| **Memory (10K vectors)** | 50 MB | 100 MB |
| **Memory (1M vectors)** | 1.5 GB | 2 GB |
| **Insert Speed** | Very fast | Fast |
| **Update/Delete** | Difficult | Easy |
| **Filtering** | Manual | Native |
| **Scalability** | Medium | Excellent |

## Advanced Features

### Milvus-Only Features

When using Milvus, you get additional capabilities:

1. **Filtered Search** (coming soon)
```python
# Search with metadata filters
results = store.search_with_filter(
    query_vector,
    filter_expr='page_number > 100 and source like "*.pdf"',
    top_k=5
)
```

2. **Dynamic Schema** (coming soon)
```python
# Add new fields without rebuilding
store.add_field('timestamp', DataType.INT64)
```

3. **Monitoring** (built-in)
```python
# Check system stats
stats = store.get_stats()
print(stats['is_loaded'])  # Collection load status
```

## Best Practices

1. **Start with FAISS**: Use for development and testing
2. **Migrate to Milvus**: When you hit these triggers:
   - Vector count > 500K
   - Need concurrent users
   - Need production SLA
   - Need advanced filtering
3. **Use Environment Variables**: Keep config in `.env`, not hardcoded
4. **Abstract Your Code**: Use the factory pattern, don't create stores directly
5. **Test Both**: Verify your code works with both backends

## Next Steps

- ✅ Configuration complete
- ✅ Choose vector database type
- ✅ Update `.env` file
- ✅ Install dependencies if using Milvus
- ✅ Start Milvus server if needed
- ✅ Test your setup
- ✅ Run document ingestion
- ✅ Start querying!

## Support

For issues:
- **FAISS**: Check FAISS documentation at https://github.com/facebookresearch/faiss
- **Milvus**: Check Milvus docs at https://milvus.io/docs
- **This Project**: See main README.md or contact team lead
