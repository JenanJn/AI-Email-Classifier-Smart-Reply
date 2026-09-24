# =============================================================================
# Train the ML email classifier
# Run from project root: .\train_model.ps1
# =============================================================================

$ProjectRoot = $PSScriptRoot
Set-Location "$ProjectRoot\backend"

Write-Host ""
Write-Host "Training ML Email Classifier (TF-IDF + Linear SVC)..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

python -m scripts.train_classifier

Write-Host ""
Write-Host "Model saved to backend/app/ml/models/email_classifier.pkl" -ForegroundColor Green
Set-Location $ProjectRoot
