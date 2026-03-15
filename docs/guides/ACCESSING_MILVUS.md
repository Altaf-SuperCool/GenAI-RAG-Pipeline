# How to Access Milvus Database

Complete guide to accessing and interacting with your Milvus vector database.

## Prerequisites Check

Before accessing Milvus, ensure:

1. **Docker Desktop is running**
   ```powershell
   # Check if Docker is running
   docker info
   ```

2. **Milvus containers are started**
   ```powershell
   # Start Milvus
   docker-compose up -d
   
   # Verify status
   docker-compose ps
   ```

Expected output:
```
NAME                IMAGE                    STATUS
milvus-standalone   milvusdb/milvus:v2.4.0   Up (healthy)
milvus-attu         zilliz/attu:v2.4         Up
```

## Method 1: Web UI (Attu) - Recommended for Beginners 🌐

**Attu** is the official web-based GUI for Milvus - easiest way to explore your data!

### Step 1: Start Milvus
```powershell
docker-compose up -d
```

### Step 2: Open Attu
Open your browser and go to: **http://localhost:8000**

### Step 3: Connect
**Connection Settings:**
- **Milvus Address**: `milvus-standalone:19530` (or `localhost:19530`)
- Click **Connect**

### What You Can Do in Attu:
- ✅ Browse all collections (tables)
- ✅ View collection schemas and statistics
- ✅ Search and query vectors
- ✅ Manage indices
- ✅ Monitor performance
- ✅ Execute queries visually
- ✅ View sample data

### Quick Tour:
1. **Collections Tab** - See all your vector collections
2. **Query** - Run similarity searches
3. **Console** - Execute Python/CLI commands
4. **System View** - Monitor health and performance

## Method 2: Python API - Programmatic Access 🐍

### Basic Connection

```python
from pymilvus import connections, Collection

# Connect to Milvus
connections.connect(
    alias="default",
    host="localhost",
    port=19530
)

print("✅ Connected to Milvus!")
```

### List All Collections

```python
from pymilvus import utility

# Get all collection names
collections = utility.list_collections()
print(f"Collections: {collections}")
```

### Access Your RAG Collection

```python
from pymilvus import Collection

# Load your collection
collection_name = "devops_knowledgebase"
collection = Collection(collection_name)
collection.load()

# Get statistics
print(f"Collection: {collection_name}")
print(f"Total vectors: {collection.num_entities}")
print(f"Schema: {collection.schema}")
```

### Search Vectors

```python
import numpy as np
from pymilvus import Collection

# Load collection
collection = Collection("devops_knowledgebase")
collection.load()

# Create a sample query vector (384 dimensions for your embeddings)
query_vector = np.random.rand(384).tolist()

# Search
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
results = collection.search(
    data=[query_vector],
    anns_field="embedding",
    param=search_params,
    limit=5,
    output_fields=["text", "source", "chunk_id"]
)

# Display results
for hits in results:
    for hit in hits:
        print(f"Distance: {hit.distance}")
        print(f"ID: {hit.id}")
        print(f"Data: {hit.entity}")
        print("---")
```

### Query with Filters

```python
# Query with metadata filtering
expr = "source == 'document.pdf'"
results = collection.query(
    expr=expr,
    output_fields=["text", "source", "chunk_id"],
    limit=10
)

for result in results:
    print(result)
```

## Method 3: Using RAG Vector Store Abstraction 🏭

**Easiest for RAG System** - Uses your existing implementation:

```python
from src.vector_store_factory import get_vector_store
from src.embedding import EmbeddingManager

# Get Milvus store
store = get_vector_store(store_type='milvus')
store.initialize()

print(f"Total vectors: {store.total_vectors}")

# Search with your actual embedding manager
embedding_manager = EmbeddingManager()
query = "What is DevOps?"
query_vector = embedding_manager.embed_query(query)

results = store.search([query_vector], top_k=5)

for result in results:
    print(f"Distance: {result['distance']}")
    print(f"Source: {result['metadata']['source']}")
    print(f"Text: {result['metadata']['text'][:200]}...")
    print("---")
```

## Method 4: Interactive Python Session 💻

### Quick Access Script

Create a file `quick_milvus_access.py`:

```python
"""
Quick Milvus Database Access
Run: python quick_milvus_access.py
"""
from pymilvus import connections, Collection, utility

# Connect
connections.connect("default", host="localhost", port=19530)
print("✅ Connected to Milvus\n")

# List collections
collections = utility.list_collections()
print(f"📚 Collections ({len(collections)}):")
for coll_name in collections:
    coll = Collection(coll_name)
    coll.load()
    print(f"  • {coll_name}: {coll.num_entities:,} vectors")

# Access main collection
if "devops_knowledgebase" in collections:
    collection = Collection("devops_knowledgebase")
    collection.load()
    
    print(f"\n📊 Collection: devops_knowledgebase")
    print(f"   Total vectors: {collection.num_entities:,}")
    print(f"\n   Schema:")
    for field in collection.schema.fields:
        print(f"     - {field.name}: {field.dtype}")
    
    # Sample data
    print(f"\n   Sample data (first 3 records):")
    results = collection.query(
        expr="",
        output_fields=["text", "source"],
        limit=3
    )
    for i, result in enumerate(results, 1):
        print(f"\n   Record {i}:")
        print(f"     Source: {result.get('source', 'N/A')}")
        text = result.get('text', 'N/A')
        print(f"     Text: {text[:100]}...")

print("\n✅ Access complete!")
```

Run it:
```powershell
python quick_milvus_access.py
```

## Method 5: Command Line Tools 🔧

### Check Milvus Health

```powershell
# Health check endpoint
curl http://localhost:9091/healthz

# Or in PowerShell
Invoke-WebRequest http://localhost:9091/healthz
```

### View Milvus Logs

```powershell
# Real-time logs
docker-compose logs -f milvus-standalone

# Last 100 lines
docker-compose logs --tail=100 milvus-standalone
```

### Milvus CLI (Optional)

Install Milvus CLI:
```powershell
pip install milvus-cli
```

Connect and interact:
```powershell
milvus_cli

# In CLI:
connect -h localhost -p 19530
list collections
show collection -c devops_knowledgebase
```

## Common Tasks

### Check Collection Status

```python
from pymilvus import Collection, utility

# Check if collection exists
exists = utility.has_collection("devops_knowledgebase")
print(f"Collection exists: {exists}")

if exists:
    collection = Collection("devops_knowledgebase")
    collection.load()
    
    # Get detailed stats
    print(f"Vectors: {collection.num_entities}")
    print(f"Has index: {collection.has_index()}")
    print(f"Is loaded: {collection.is_loaded}")
```

### Export Data

```python
from pymilvus import Collection

collection = Collection("devops_knowledgebase")
collection.load()

# Export all data
results = collection.query(
    expr="",
    output_fields=["text", "source", "chunk_id"],
    limit=10000  # Adjust as needed
)

# Save to file
import json
with open("milvus_export.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Exported {len(results)} records")
```

### Backup Collection

```powershell
# Stop Milvus
docker-compose stop

# Backup data directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Recurse milvus_data "milvus_backup_$timestamp"

# Start Milvus
docker-compose start

Write-Host "✅ Backup created: milvus_backup_$timestamp"
```

## Troubleshooting Access Issues

### Cannot Connect

**Problem:** Connection refused or timeout

**Solutions:**
```powershell
# 1. Check if Milvus is running
docker-compose ps

# 2. Check if port is open
Test-NetConnection localhost -Port 19530

# 3. Restart Milvus
docker-compose restart milvus-standalone

# 4. Check logs for errors
docker-compose logs milvus-standalone | Select-String "error"
```

### Attu Won't Load

**Problem:** Web UI doesn't open

**Solutions:**
```powershell
# 1. Check Attu container
docker-compose ps milvus-attu

# 2. Restart Attu
docker-compose restart milvus-attu

# 3. Check port 8000
Test-NetConnection localhost -Port 8000

# 4. View Attu logs
docker-compose logs milvus-attu
```

### "Collection Not Found"

**Problem:** Collection doesn't exist

**Solutions:**
```python
from pymilvus import utility

# List all collections
print(utility.list_collections())

# Run migration if collection is missing
# python scripts/migrate_faiss_to_milvus.py
```

### Authentication Errors

Milvus standalone doesn't require authentication by default. If you see auth errors:

```python
# Connect without auth (default)
connections.connect(
    alias="default",
    host="localhost",
    port=19530
    # No user/password needed
)
```

## Quick Reference

### Connection Details
- **Host**: `localhost` (or `milvus-standalone` from Docker network)
- **Port**: `19530` (gRPC)
- **Health Check Port**: `9091`
- **Attu Web UI**: `http://localhost:8000`

### Default Collection
- **Name**: `devops_knowledgebase`
- **Dimension**: `384`
- **Metric**: `L2` (Euclidean distance)
- **Fields**: `id`, `embedding`, `text`, `source`, `chunk_id`

### Python Quick Access
```python
from pymilvus import connections, Collection
connections.connect("default", host="localhost", port=19530)
collection = Collection("devops_knowledgebase")
collection.load()
print(f"Vectors: {collection.num_entities}")
```

### Docker Quick Commands
```powershell
docker-compose up -d        # Start
docker-compose ps           # Status
docker-compose logs -f      # Logs
docker-compose stop         # Stop
docker-compose restart      # Restart
```

## Best Practices

1. **Always Load Collection Before Use**
   ```python
   collection.load()  # Required before search/query
   ```

2. **Close Connections When Done**
   ```python
   connections.disconnect("default")
   ```

3. **Use Attu for Exploration** - Great for understanding your data structure

4. **Use Python API for Automation** - Best for scripts and applications

5. **Monitor Resource Usage** - Check Docker Desktop for CPU/memory

6. **Regular Backups** - Backup `milvus_data/` folder periodically

## Next Steps

1. ✅ Access Attu: http://localhost:8000
2. ✅ Run quick access script: `python quick_milvus_access.py`
3. ✅ Explore your collection in Attu
4. ✅ Try searching vectors with Python
5. ✅ Integrate with your RAG system

## Additional Resources

- **Milvus Python SDK**: https://milvus.io/docs/install-pymilvus.md
- **Attu Guide**: https://github.com/zilliz/attu
- **API Reference**: https://milvus.io/api-reference/pymilvus/v2.4.x/About.md
- **Search Tutorials**: https://milvus.io/docs/search.md

---

**Need Help?** Check Milvus logs or see [MILVUS_SETUP.md](./MILVUS_SETUP.md) for troubleshooting.
