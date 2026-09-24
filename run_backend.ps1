# =============================================================================
# Start the FastAPI backend server
# Run from project root: .\run_backend.ps1
# =============================================================================

$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$DbPath = Join-Path $BackendDir "email_classifier.db"

Write-Host ""
Write-Host "Starting AI Email Classifier Backend..." -ForegroundColor Cyan
Write-Host "API:  http://localhost:8000" -ForegroundColor Green
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# Activate venv if it exists
if (Test-Path (Join-Path $BackendDir ".venv\Scripts\Activate.ps1")) {
    & (Join-Path $BackendDir ".venv\Scripts\Activate.ps1")
} else {
    Write-Host "WARNING: .venv not found. Run .\setup.ps1 first." -ForegroundColor Yellow
}

# Set absolute DB path to avoid CWD issues
$env:DATABASE_URL = "sqlite+aiosqlite:///$($DbPath -replace '\\','/')"
$env:DATABASE_URL_SYNC = "sqlite:///$($DbPath -replace '\\','/')"

Set-Location $BackendDir

# Start uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
