# =============================================================================
# Run all backend tests
# Run from project root: .\run_tests.ps1
# =============================================================================

$ProjectRoot = $PSScriptRoot
Set-Location "$ProjectRoot\backend"

Write-Host ""
Write-Host "Running AI Email Classifier Tests..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

# Force in-memory SQLite for tests
$env:DATABASE_URL = "sqlite+aiosqlite:///:memory:"
$env:DATABASE_URL_SYNC = "sqlite:///:memory:"

pytest tests/ -v --tb=short

Write-Host ""
Set-Location $ProjectRoot
