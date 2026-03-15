# Milvus Standalone Setup Guide

Complete guide to setting up and using Milvus vector database with your RAG system.

## Table of Contents
- [Why Milvus?](#why-milvus)
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Migration from FAISS](#migration-from-faiss)
- [Verification](#verification)
- [Management](#management)
- [Troubleshooting](#troubleshooting)

## Why Milvus?

### FAISS vs Milvus Comparison

| Feature | FAISS | Milvus |
|---------|-------|--------|
| **Scale** | < 1M vectors | 1M+ vectors |
| **Architecture** | Single machine, file-based | Distributed, server-based |
| **Metadata** | Manual management | Native support |
| **Filtering** | Limited | Advanced filtering |
| **Updates** | Rebuild required | Dynamic updates |
| **Persistence** | File system | Database with WAL |
| **Monitoring** | None | Web UI (Attu) |
| **Performance** | Fast for small datasets | Optimized for large scale |

**Use FAISS when:**
- Dataset < 1 million vectors
- Single machine deployment
- Simple similarity search

**Use Milvus when:**
- Dataset > 1 million vectors
- Need dynamic updates
- Production deployment
- Advanced filtering required
- Team needs web UI

## Prerequisites

### 1. Docker Desktop (Windows)

**Install Docker Desktop:**
1. Download from: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Start Docker Desktop
4. Verify installation:
```powershell
docker --version
docker-compose --version
```

### 2. Install Milvus Python Client

```powershell
pip install pymilvus
```

### 3. System Requirements

- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk**: 10GB+ free space
- **CPU**: 2+ cores recommended
- **OS**: Windows 10/11 with WSL2 enabled

## Installation Steps

### Step 1: Start Milvus Standalone

#### Option A: Using Docker Compose (Recommended)

The project includes a `docker-compose.yml` file with Milvus and Attu (Web UI).

```powershell
# Navigate to project root
cd C:\Users\v193570\Documents\GitHub\United.CYA.DevSecOps.Agentic.AI.RAG

# Start Milvus (detached mode)
docker-compose up -d

# Check status
docker-compose ps
```

**Expected Output:**
```
NAME                IMAGE                    STATUS
milvus-standalone   milvusdb/milvus:v2.4.0   Up (healthy)
milvus-attu         zilliz/attu:v2.4         Up
```

#### Option B: Using Docker Run

```powershell
# Create data directory
mkdir milvus_data

# Run Milvus
docker run -d `
  --name milvus-standalone `
  -p 19530:19530 `
  -p 9091:9091 `
  -v ${PWD}/milvus_data:/var/lib/milvus `
  -e ETCD_USE_EMBED=true `
  -e COMMON_STORAGETYPE=local `
  milvusdb/milvus:v2.4.0 `
  milvus run standalone
```

### Step 2: Verify Milvus is Running

```powershell
# Check Docker logs
docker logs milvus-standalone

# Test connection
python -c "from pymilvus import connections; connections.connect('default', host='localhost', port=19530); print('✅ Connected to Milvus!')"
```

### Step 3: Access Attu Web UI (Optional)

Open your browser and go to: **http://localhost:8000**

**Login Details:**
- Host: `milvus-standalone`
- Port: `19530`

You can browse collections, view statistics, and manage your vector database through the web interface.

## Configuration

### Update Environment Variables

Edit your `.env` file in the project root:

```bash
# ===== Vector Database Configuration =====
# Switch from FAISS to Milvus
VECTOR_DB_TYPE=milvus

# Milvus Connection Settings
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=devops_knowledgebase
```

### Verify Configuration

```powershell
# Test the configuration
python -c "from src.vector_store_factory import get_vector_store; store = get_vector_store(); print('✅ Vector store configured:', type(store).__name__)"
```

**Expected Output:**
```
[FACTORY] Creating Milvus vector store...
[MILVUS] Initialized with collection='devops_knowledgebase', host=localhost:19530
✅ Vector store configured: MilvusVectorStore
```

## Migration from FAISS

### Automatic Migration Script

Use the provided migration script to transfer your existing vectors from FAISS to Milvus:

```powershell
# Run migration script
python scripts/migrate_faiss_to_milvus.py
```

The script will:
1. Load vectors from FAISS (`data/vector_store/`)
2. Connect to Milvus
3. Create collection if it doesn't exist
4. Transfer all vectors with metadata
5. Create indices for optimal performance
6. Verify the migration

### Manual Migration

If you prefer manual control:

```python
from src.faiss_store import FaissVectorStore
from src.milvus_store import MilvusVectorStore

# Load from FAISS
faiss_store = FaissVectorStore()
faiss_store.load()

# Initialize Milvus
milvus_store = MilvusVectorStore()
milvus_store.initialize()

# Get all vectors and metadata
vectors = []
metadata_list = []
for i in range(faiss_store.total_vectors):
    # Extract vectors and metadata from FAISS
    # Add to Milvus
    pass

# Add to Milvus
milvus_store.add(vectors, metadata_list)
print(f"✅ Migrated {len(vectors)} vectors to Milvus")
```

## Verification

### Test Vector Store

```powershell
# Run test script
python tests/test_milvus.py
```

### Test RAG System

```powershell
# Test the complete RAG pipeline with Milvus
python tests/test_rag_chat.py
```

### Check Collection Statistics

```python
from pymilvus import Collection, connections

connections.connect('default', host='localhost', port=19530)
collection = Collection('devops_knowledgebase')
collection.load()

print(f"Total vectors: {collection.num_entities}")
print(f"Collection schema: {collection.schema}")
```

## Management

### Common Operations

#### Start Milvus
```powershell
docker-compose start
```

#### Stop Milvus
```powershell
docker-compose stop
```

#### Restart Milvus
```powershell
docker-compose restart
```

#### View Logs
```powershell
docker-compose logs -f milvus-standalone
```

#### Stop and Remove (Keeps Data)
```powershell
docker-compose down
```

#### Complete Removal (Deletes Data)
```powershell
docker-compose down -v
Remove-Item -Recurse -Force milvus_data
```

### Backup and Restore

#### Backup
```powershell
# Stop Milvus
docker-compose stop

# Backup data directory
Copy-Item -Recurse milvus_data milvus_data_backup_$(Get-Date -Format 'yyyyMMdd')

# Start Milvus
docker-compose start
```

#### Restore
```powershell
# Stop Milvus
docker-compose stop

# Restore data
Remove-Item -Recurse -Force milvus_data
Copy-Item -Recurse milvus_data_backup_YYYYMMDD milvus_data

# Start Milvus
docker-compose start
```

## Troubleshooting

### Milvus Won't Start

**Problem:** Docker container fails to start

**Solutions:**
```powershell
# Check Docker Desktop is running
Get-Process "Docker Desktop"

# Check port availability
netstat -ano | findstr "19530"

# View detailed logs
docker logs milvus-standalone

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Connection Refused

**Problem:** Cannot connect to Milvus from Python

**Solutions:**
```powershell
# Verify Milvus is healthy
docker-compose ps

# Test network connectivity
Test-NetConnection localhost -Port 19530

# Check firewall settings
# Windows Defender Firewall -> Allow app -> Docker Desktop

# Verify pymilvus is installed
pip show pymilvus
```

### Slow Performance

**Problem:** Queries are slow

**Solutions:**
1. **Create Index:**
```python
from pymilvus import Collection, connections

connections.connect('default', host='localhost', port=19530)
collection = Collection('devops_knowledgebase')

# Create IVF_FLAT index
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128}
}
collection.create_index(field_name="embedding", index_params=index_params)
collection.load()
```

2. **Increase Docker Resources:**
   - Docker Desktop Settings → Resources
   - Increase CPU cores to 4+
   - Increase Memory to 4GB+

3. **Optimize Search Parameters:**
```python
# Use search parameters for speed/accuracy tradeoff
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
results = collection.search(vectors, "embedding", search_params, limit=5)
```

### Out of Memory

**Problem:** Milvus crashes with OOM

**Solutions:**
1. Increase Docker memory limit (Docker Desktop Settings)
2. Reduce collection size
3. Use disk-based index instead of memory-based

### Port Already in Use

**Problem:** Port 19530 is already occupied

**Solutions:**
```powershell
# Find process using port
netstat -ano | findstr "19530"

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# ports:
#   - "19531:19530"  # Use different external port
```

## Performance Tuning

### Index Selection

Milvus supports multiple index types. Choose based on your needs:

| Index Type | Speed | Accuracy | Memory | Best For |
|------------|-------|----------|---------|----------|
| **FLAT** | Slow | 100% | High | Small datasets (<10K) |
| **IVF_FLAT** | Fast | 95-99% | Medium | Medium datasets (10K-1M) |
| **IVF_SQ8** | Faster | 95-98% | Low | Large datasets, memory constrained |
| **HNSW** | Very Fast | 98-99% | Highest | High-performance needs |

### Recommended Settings for RAG

```python
# For 4K vectors (current dataset)
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 64}  # sqrt(4000) ≈ 64
}

search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 10}  # 10-20% of nlist
}
```

## Next Steps

1. ✅ Milvus is running
2. ✅ Configuration updated
3. ✅ Data migrated
4. 🔄 Test your RAG system:
   ```powershell
   python src/chat/web_chat.py
   ```
5. 📊 Monitor via Attu: http://localhost:8000

## Additional Resources

- **Milvus Documentation**: https://milvus.io/docs
- **Milvus GitHub**: https://github.com/milvus-io/milvus
- **Attu Web UI**: https://github.com/zilliz/attu
- **Python SDK**: https://milvus.io/docs/install-pymilvus.md

## Support

For issues specific to this implementation:
- Check logs: `docker-compose logs milvus-standalone`
- Verify connection: `python tests/test_milvus.py`
- Review error messages in console output

For Milvus-specific questions:
- Milvus Community: https://discuss.milvus.io
- GitHub Issues: https://github.com/milvus-io/milvus/issues
