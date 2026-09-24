# =============================================================================
# AI Email Classifier — Full Setup Script (Windows PowerShell)
# Run from the project root: .\setup.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  AI Email Classifier — Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Check Python ───────────────────────────────────────────────────────────
Write-Host "[1/7] Checking Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "      Found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Python not found. Install Python 3.11+ from https://python.org" -ForegroundColor Red
    exit 1
}

# ── 2. Check Node ─────────────────────────────────────────────────────────────
Write-Host "[2/7] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "      Found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Node.js not found. Install Node 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# ── 3. Backend virtual environment ────────────────────────────────────────────
Write-Host "[3/7] Setting up Python virtual environment..." -ForegroundColor Yellow
Set-Location "$ProjectRoot\backend"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "      Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "      Virtual environment already exists." -ForegroundColor Green
}

# Activate venv
& ".venv\Scripts\Activate.ps1"

# ── 4. Install Python dependencies ────────────────────────────────────────────
Write-Host "[4/7] Installing Python dependencies..." -ForegroundColor Yellow
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
Write-Host "      Python dependencies installed." -ForegroundColor Green

# ── 5. Download spaCy model ───────────────────────────────────────────────────
Write-Host "[5/7] Downloading spaCy language model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm --quiet
Write-Host "      spaCy en_core_web_sm ready." -ForegroundColor Green

# ── 6. Download NLTK data ─────────────────────────────────────────────────────
Write-Host "[5b]  Downloading NLTK data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"
Write-Host "      NLTK data ready." -ForegroundColor Green

# ── 7. Train ML classifier ────────────────────────────────────────────────────
Write-Host "[6/7] Training ML email classifier..." -ForegroundColor Yellow
python -m scripts.train_classifier
Write-Host "      ML classifier trained and saved." -ForegroundColor Green

# ── 8. Seed database ─────────────────────────────────────────────────────────
Write-Host "[7/7] Initialising database and seeding sample data..." -ForegroundColor Yellow
$DbPath = Join-Path $ProjectRoot "backend\email_classifier.db"
$env:DATABASE_URL = "sqlite+aiosqlite:///$($DbPath -replace '\\','/')"
$env:DATABASE_URL_SYNC = "sqlite:///$($DbPath -replace '\\','/')"
python -m scripts.seed_db
Write-Host "      Database seeded with sample emails." -ForegroundColor Green

# Ensure password hash is compatible with current bcrypt version
$fixScript = @"
import sys, sqlite3
sys.path.insert(0, '.')
from app.core.security import hash_password, verify_password
db = '$($DbPath -replace "\\","/")'
conn = sqlite3.connect(db)
row = conn.execute('SELECT hashed_password FROM users WHERE email=?', ['demo@emailai.com']).fetchone()
if row and not verify_password('demo1234', row[0]):
    h = hash_password('demo1234')
    conn.execute('UPDATE users SET hashed_password=? WHERE email=?', [h, 'demo@emailai.com'])
    conn.commit()
    print('Password hash updated for bcrypt compatibility.')
else:
    print('Password hash is valid.')
conn.close()
"@
python -c $fixScript

# ── 9. Frontend dependencies ──────────────────────────────────────────────────
Write-Host ""
Write-Host "[+]   Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "$ProjectRoot\frontend"
npm install --silent
Write-Host "      Frontend dependencies installed." -ForegroundColor Green

Set-Location $ProjectRoot

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run the backend:   .\run_backend.ps1" -ForegroundColor White
Write-Host "  2. Run the frontend:  .\run_frontend.ps1" -ForegroundColor White
Write-Host "  3. Open browser:      http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "  Demo login:" -ForegroundColor Cyan
Write-Host "    Email:    demo@emailai.com" -ForegroundColor White
Write-Host "    Password: demo1234" -ForegroundColor White
Write-Host ""
