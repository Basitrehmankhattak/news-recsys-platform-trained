# Start MongoDB Server
Write-Host "Starting MongoDB..." -ForegroundColor Green

$mongoPath = "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe"
$dataPath = "C:\data\db"

# Check if MongoDB exists
if (-not (Test-Path $mongoPath)) {
    Write-Host "Error: MongoDB not found at $mongoPath" -ForegroundColor Red
    exit 1
}

# Create data directory if it doesn't exist
if (-not (Test-Path $dataPath)) {
    New-Item -ItemType Directory -Force -Path $dataPath | Out-Null
    Write-Host "Created data directory: $dataPath" -ForegroundColor Yellow
}

# Start MongoDB
Write-Host "Launching MongoDB on port 27017..." -ForegroundColor Cyan
Write-Host "Data directory: $dataPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "MongoDB is starting... Keep this window open!" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop MongoDB" -ForegroundColor Yellow
Write-Host ""

& $mongoPath --dbpath $dataPath
