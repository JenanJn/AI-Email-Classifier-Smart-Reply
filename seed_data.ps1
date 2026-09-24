# =============================================================================
# Re-seed the database with sample emails
# Run from project root: .\seed_data.ps1
# =============================================================================

$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$DbPath = Join-Path $BackendDir "email_classifier.db"

Write-Host ""
Write-Host "Seeding database with sample emails..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path (Join-Path $BackendDir ".venv\Scripts\Activate.ps1")) {
    & (Join-Path $BackendDir ".venv\Scripts\Activate.ps1")
}

Set-Location $BackendDir

# Set absolute DB path
$env:DATABASE_URL = "sqlite+aiosqlite:///$($DbPath -replace '\\','/')"
$env:DATABASE_URL_SYNC = "sqlite:///$($DbPath -replace '\\','/')"

# Remove old DB for clean seed
if (Test-Path $DbPath) {
    Remove-Item $DbPath -Force
    Write-Host "Old database removed." -ForegroundColor Yellow
}

python -m scripts.seed_db

Write-Host ""
Write-Host "Demo login: demo@emailai.com / demo1234" -ForegroundColor Green
Set-Location $ProjectRoot
