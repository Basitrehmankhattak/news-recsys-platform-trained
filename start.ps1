# News Recommendation System - Startup Script
# Run this after Docker Desktop is installed and running

Write-Host " Starting News Recommendation System..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Start PostgreSQL with Docker
Write-Host " Step 1: Starting PostgreSQL container..." -ForegroundColor Yellow
docker compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host " PostgreSQL container started successfully!" -ForegroundColor Green
} else {
    Write-Host " Failed to start PostgreSQL. Make sure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

# Wait for PostgreSQL to be ready
Write-Host ""
Write-Host " Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 2: Check if migrations need to be run
Write-Host ""
Write-Host " Step 2: Checking database schema..." -ForegroundColor Yellow

# Try to run migrations using PowerShell-compatible syntax
Write-Host "Running database migrations..." -ForegroundColor Yellow
Get-Content migrations/001_init_schema.sql | docker compose exec -T postgres psql -U newsrec -d newsrec 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host " Database schema initialized!" -ForegroundColor Green
} else {
    Write-Host "  Migrations may have already been run (this is OK)" -ForegroundColor Yellow
}

# Step 3: Install backend dependencies
Write-Host ""
Write-Host " Step 3: Installing backend dependencies..." -ForegroundColor Yellow
pip install -q -r backend/requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host " Backend dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Install frontend dependencies
Write-Host ""
Write-Host " Step 4: Checking frontend dependencies..." -ForegroundColor Yellow
pip install -q -r frontend/requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host " Frontend dependencies ready!" -ForegroundColor Green
} else {
    Write-Host " Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Setup Complete! Ready to start the application." -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host " Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Start the Backend (in this terminal):" -ForegroundColor White
Write-Host "   uvicorn backend.app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "2️⃣  Start the Frontend (in a NEW terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   streamlit run app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3️⃣  Open your browser:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
