# =============================================================================
# Start the React frontend dev server
# Run from project root: .\run_frontend.ps1
# =============================================================================

$ProjectRoot = $PSScriptRoot
Set-Location "$ProjectRoot\frontend"

Write-Host ""
Write-Host "Starting AI Email Classifier Frontend..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:5173" -ForegroundColor Green
Write-Host ""

if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
}

npm run dev
