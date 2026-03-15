# Milvus Quick Start Guide

This is a streamlined guide to get Milvus up and running quickly.

## One-Command Setup (Windows)

Run the automated setup script:

```powershell
.\scripts\setup_milvus.ps1
```

This script will:
1. ✅ Check Docker installation
2. ✅ Start Milvus and Attu containers
3. ✅ Install pymilvus Python package
4. ✅ Test the connection
5. ✅ Display next steps

## Manual Setup (5 minutes)

### 1. Install Docker Desktop
Download and install from: https://www.docker.com/products/docker-desktop/

### 2. Start Milvus
```powershell
docker-compose up -d
```

### 3. Install Python Client
```powershell
pip install pymilvus
```

### 4. Test Connection
```powershell
python tests/test_milvus.py
```

## Migrate from FAISS

If you have existing FAISS data:

```powershell
# Migrate all vectors
python scripts/migrate_faiss_to_milvus.py

# Update .env
# Change: VECTOR_DB_TYPE=faiss
# To:     VECTOR_DB_TYPE=milvus
```

## Use Milvus

### Update Configuration

Edit `.env`:
```bash
VECTOR_DB_TYPE=milvus
```

### Test RAG System
```powershell
python src/chat/web_chat.py
```

## Access Web UI

Open in browser: **http://localhost:8000**

Login to Attu:
- **Host**: milvus-standalone
- **Port**: 19530

## Management

### View Status
```powershell
docker-compose ps
```

### View Logs
```powershell
docker-compose logs -f milvus-standalone
```

### Stop Milvus
```powershell
docker-compose stop
```

### Restart Milvus
```powershell
docker-compose restart
```

### Remove Everything (including data)
```powershell
docker-compose down -v
```

## Troubleshooting

### Port Already in Use
```powershell
# Find what's using port 19530
netstat -ano | findstr "19530"

# Kill the process or change port in docker-compose.yml
```

### Connection Refused
```powershell
# Check if Milvus is healthy
docker-compose ps

# View logs
docker-compose logs milvus-standalone

# Restart
docker-compose restart
```

### Slow Performance
- Increase Docker Desktop resources (Settings → Resources)
- Recommended: 4 CPU cores, 4GB RAM

## Need More Help?

See detailed documentation: [docs/guides/MILVUS_SETUP.md](./MILVUS_SETUP.md)

## Quick Reference

**Ports:**
- Milvus Server: `19530`
- Attu Web UI: `8000`
- Health Check: `9091`

**Default Collection:**
- Name: `devops_knowledgebase`
- Dimension: `384`
- Metric: `L2`

**Environment Variables:**
```bash
VECTOR_DB_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=devops_knowledgebase
```
