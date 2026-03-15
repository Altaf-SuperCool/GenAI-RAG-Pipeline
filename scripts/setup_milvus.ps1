# Milvus Quick Setup Script for Windows
# Automates the Milvus standalone setup process

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Milvus Standalone Setup for RAG System" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running with Docker
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerVersion = docker --version
    Write-Host "  ✓ Docker found: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Docker not found!" -ForegroundColor Red
    Write-Host "  Please install Docker Desktop for Windows:" -ForegroundColor Red
    Write-Host "  https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "  ✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is available
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ docker-compose is available" -ForegroundColor Green
} else {
    Write-Host "  ✗ docker-compose not found!" -ForegroundColor Red
    Write-Host "  It should come with Docker Desktop. Please reinstall Docker." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Stop any existing Milvus containers
Write-Host "Step 2: Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null | Out-Null
Write-Host "  ✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# Start Milvus
Write-Host "Step 3: Starting Milvus standalone..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes on first run..." -ForegroundColor Gray
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Milvus containers started" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to start Milvus" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Wait for Milvus to be ready
Write-Host "Step 4: Waiting for Milvus to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and -not $ready) {
    $attempt++
    Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9091/healthz" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if ($ready) {
    Write-Host "  ✓ Milvus is ready!" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Milvus may still be starting up" -ForegroundColor Yellow
    Write-Host "  Check status with: docker-compose ps" -ForegroundColor Gray
}

Write-Host ""

# Install pymilvus if needed
Write-Host "Step 5: Checking pymilvus installation..." -ForegroundColor Yellow
$pymilvusInstalled = python -c "import pymilvus; print('yes')" 2>$null

if ($pymilvusInstalled -eq "yes") {
    Write-Host "  ✓ pymilvus is already installed" -ForegroundColor Green
} else {
    Write-Host "  Installing pymilvus..." -ForegroundColor Yellow
    pip install pymilvus
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ pymilvus installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install pymilvus" -ForegroundColor Red
        Write-Host "  Try manually: pip install pymilvus" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test connection
Write-Host "Step 6: Testing Milvus connection..." -ForegroundColor Yellow
python tests/test_milvus.py 2>$null

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Services:" -ForegroundColor Yellow
Write-Host "  • Milvus Server:  http://localhost:19530" -ForegroundColor White
Write-Host "  • Attu Web UI:    http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open Attu Web UI to browse your data:" -ForegroundColor White
Write-Host "     http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Migrate data from FAISS (if you have existing data):" -ForegroundColor White
Write-Host "     python scripts/migrate_faiss_to_milvus.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Update .env file to use Milvus:" -ForegroundColor White
Write-Host "     VECTOR_DB_TYPE=milvus" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Test your RAG system:" -ForegroundColor White
Write-Host "     python src/chat/web_chat.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛠️  Management Commands:" -ForegroundColor Yellow
Write-Host "  • View logs:     docker-compose logs -f milvus-standalone" -ForegroundColor White
Write-Host "  • Stop Milvus:   docker-compose stop" -ForegroundColor White
Write-Host "  • Start Milvus:  docker-compose start" -ForegroundColor White
Write-Host "  • Remove all:    docker-compose down -v" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
