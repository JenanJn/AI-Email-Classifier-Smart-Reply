# AI-Based Email Classifier and Smart Reply Generator

 AI / ML / NLP / Generative AI / Cloud / Big Data / DBMS

An intelligent email management system that classifies incoming emails, detects intent, scores priority, extracts entities, generates contextual smart replies, and explains every AI decision — built as an **AI Email Command Center**, not a generic inbox clone.

---

## Project Overview

| Course | Component |
|--------|-----------|
| **AI / Machine Learning** | TF-IDF + Linear SVC email category classifier |
| **NLP** | spaCy entity extraction, VADER sentiment, intent detection pipeline |
| **Generative AI** | Google Gemini 1.5 Flash smart reply generation |
| **Database Management** | PostgreSQL / SQLite with normalized relational schema |
| **Cloud Computing** | Dockerized microservices, cloud-ready (Vercel + Render + Supabase) |
| **Big Data Analytics** | Extensible analytics service with category/priority/trend aggregations |

---

## Features

- **14-category email classifier** (Job, Finance, Education, Travel, Healthcare, etc.)
- **Explainable priority scoring** (0–100) with human-readable reasons
- **Named entity extraction** (persons, organizations, dates, times, amounts)
- **Intent detection** (Interview Invitation, Order Confirmation, Security Alert, etc.)
- **VADER sentiment analysis**
- **Gemini-powered smart replies** with Regenerate / Shorter / Formal / Friendly / Edit
- **Full reply version history**
- **AI Command Center dashboard** with action queue and insights
- **Analytics dashboard** with charts (category distribution, volume trends, priority by category)
- **JWT authentication**
- **REST API** with auto-generated Swagger docs at `/docs`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Charts | Recharts |
| Icons | Lucide React |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2.0 |
| ML | scikit-learn (TF-IDF + Linear SVC) |
| NLP | spaCy + NLTK + VADER Sentiment |
| Generative AI | Google Gemini 1.5 Flash |
| Database | SQLite (dev) / PostgreSQL (production) |
| Auth | JWT (python-jose + passlib) |
| Containers | Docker + Docker Compose |

---

## Project Structure

```
LA_Project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings from env vars
│   │   ├── api/routes/          # Email, Auth, Analytics, Reply, Category endpoints
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Email, Reply, Analytics services
│   │   ├── nlp/                 # NLP pipeline (preprocessor, entities, sentiment, intent)
│   │   ├── ml/                  # TF-IDF + Linear SVC classifier
│   │   ├── priority/            # Priority scoring engine + explainer
│   │   └── genai/               # Gemini prompt builder + reply generator
│   ├── data/                    # Training data + seed emails (JSON)
│   ├── scripts/                 # train_classifier.py, seed_db.py
│   ├── tests/                   # pytest test suite
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, Inbox, EmailDetail, Analytics, AddEmail, Login
│   │   ├── components/          # Layout, Email cards, AI analysis panel, Reply editor
│   │   ├── api/                 # Axios API client
│   │   ├── hooks/               # useAuth
│   │   ├── types/               # TypeScript interfaces
│   │   └── utils/               # Priority colors, date formatting, category utils
│   └── package.json
│
├── setup.ps1                    # One-command Windows setup
├── run_backend.ps1              # Start backend
├── run_frontend.ps1             # Start frontend
├── run_tests.ps1                # Run test suite
├── train_model.ps1              # Train ML classifier
├── seed_data.ps1                # Re-seed sample emails
└── docker-compose.yml           # Full stack Docker deployment
```

---

## Quick Start (Windows — Recommended)

### Prerequisites

- Python 3.11+ — https://python.org/downloads
- Node.js 18+ — https://nodejs.org
- Git (optional)

### Step 1 — Get the Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Create a free API key
3. Open `backend/.env` and paste it:
   ```
   GEMINI_API_KEY=your-key-here
   ```

### Step 2 — Run Setup (installs everything)

Open PowerShell in the project root and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Download the spaCy language model
- Download NLTK data
- Train the ML classifier
- Initialize the SQLite database
- Seed 16 realistic sample emails with full AI analysis
- Install frontend Node dependencies

### Step 3 — Start the Backend

Open a terminal in the project root:

```powershell
.\run_backend.ps1
```

API available at: http://localhost:8000
Swagger docs at: http://localhost:8000/docs

### Step 4 — Start the Frontend

Open a **second** terminal in the project root:

```powershell
.\run_frontend.ps1
```

App available at: http://localhost:5173

### Step 5 — Log In

Use the demo account that was seeded automatically:

```
Email:    demo@emailai.com
Password: demo1234
```

Or register a new account and add emails manually.

---

## Manual Setup (without scripts)

### Backend

```powershell
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Train the ML classifier
python -m scripts.train_classifier

# Seed the database
python -m scripts.seed_db

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

---

## Running Tests

```powershell
.\run_tests.ps1
```

Or manually:

```powershell
cd backend
.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "sqlite+aiosqlite:///:memory:"
pytest tests/ -v
```

Test coverage includes:
- NLP preprocessor (HTML cleaning, text normalization)
- Intent detector (interview, order, security alert, job offer patterns)
- Sentiment analyzer (positive/negative/neutral)
- Priority engine (high/medium/low scoring, action required detection, score bounds)
- ML classifier (all 14 categories, confidence range, empty input)
- API endpoints (auth, email CRUD, 401 enforcement, validation)

---

## API Reference

Full interactive docs: http://localhost:8000/docs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, receive JWT |
| POST | `/emails` | Add + auto-analyze email |
| GET | `/emails` | List with filters (category, priority, action_required, search) |
| GET | `/emails/{id}` | Full email with AI analysis |
| POST | `/emails/{id}/analyze` | Re-trigger AI analysis |
| DELETE | `/emails/{id}` | Delete email |
| POST | `/emails/{id}/reply/generate` | Generate smart reply |
| POST | `/emails/{id}/reply/regenerate` | New variation |
| POST | `/emails/{id}/reply/modify` | Style: shorter/formal/friendly/longer |
| PATCH | `/emails/{id}/reply` | Save user edit |
| GET | `/emails/{id}/reply/history` | All reply versions |
| GET | `/categories` | All email categories |
| GET | `/analytics/summary` | Inbox statistics |
| GET | `/analytics/trends?period=30` | Charts data |
| GET | `/analytics/insights` | AI-generated text insights |
| GET | `/health` | Health check |

---

## Database Schema

```
users
  └── emails
        ├── email_analysis    (category, confidence, intent, priority, sentiment, entities summary)
        ├── email_entities    (PERSON, ORG, DATE, TIME, MONEY, GPE per email)
        └── generated_replies
              └── reply_versions  (full history of every generated/edited version)

categories  (14 built-in, extensible)
```

---

## Priority Scoring System

The priority score (0–100) is computed from 8 independent signals:

| Signal | Max Score | Example Trigger |
|--------|-----------|-----------------|
| Urgency words | 15 | "urgent", "ASAP", "immediately" |
| Deadline proximity | 25 | "tomorrow", "today", "within 24 hours" |
| Action required | 15 | "please confirm", "action required" |
| Category importance | 10 | Finance/Healthcare > Promotions |
| Scheduled event | 10 | "interview scheduled", "meeting at 3 PM" |
| Security/fraud alert | 10 | "unauthorized access", "account blocked" |
| Time-sensitive language | 10 | "expires tonight", "last chance" |
| Sender importance | 5 | Organizational email domain |

Score bands: **0–39 Low** · **40–69 Medium** · **70–100 High**

---

## NLP Pipeline

```
Raw Email
    │
    ▼
Preprocessor        — strip HTML, unescape entities, normalize whitespace
    │
    ├─► Entity Extractor  — spaCy NER: PERSON, ORG, DATE, TIME, MONEY, GPE
    │
    ├─► Sentiment Analyzer — VADER compound score → positive/neutral/negative
    │
    ├─► ML Classifier     — TF-IDF (bigrams, 15k features) + Linear SVC → category + confidence
    │
    └─► Intent Detector   — 60+ regex patterns → specific intent within category
```

---

## ML Classifier Details

- **Algorithm**: TF-IDF + Linear SVC (wrapped in CalibratedClassifierCV for probability output)
- **Features**: Unigrams + bigrams, max 15,000 features, sublinear TF scaling
- **Subject weighting**: Subject repeated 2× in input text to increase its influence
- **Training data**: 70 labeled samples across 14 categories (`data/training_data.json`)
- **Evaluation**: 5-fold cross-validation, per-class precision/recall/F1 report
- **Fallback**: Keyword frequency rules when no trained model is found

To retrain after adding training samples:
```powershell
.\train_model.ps1
```

---

## Generative AI Architecture

- **Model**: Google Gemini 1.5 Flash
- **Approach**: Category-aware system prompts + dynamic context injection
- **Context provided to Gemini**: email category, intent, detected entities, deadline, action required, tone
- **Variation modes**: Regenerate (new sample), Shorter, More Formal, Friendlier, Longer
- **Fallback**: Template-based replies if API is unavailable
- **Version tracking**: Every generated/modified/edited version stored in `reply_versions`

---

## Cloud Deployment (Free Tier)

| Service | Platform | Cost |
|---------|----------|------|
| Frontend | Vercel | Free |
| Backend + NLP | Render | Free |
| Database | Supabase PostgreSQL | Free (500MB) |
| Gemini API | Google AI Studio | Free (15 RPM) |

Switch from SQLite to PostgreSQL by updating `DATABASE_URL` in `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/email_classifier
```

---

## Big Data Analytics — Scalability Path

The analytics service queries `email_analysis` using SQLAlchemy aggregations.  
As data scales, the same queries map directly to equivalent operations:

| Scale | Approach |
|-------|----------|
| < 10K emails | PostgreSQL SQL (current) |
| 10K–1M | PostgreSQL + materialized views |
| 1M+ | Export to Parquet/S3 → Apache Spark DataFrame operations |

Spark equivalent of the category distribution query:
```python
# SQLAlchemy (current)
SELECT category_name, COUNT(*) FROM email_analysis GROUP BY category_name

# PySpark (future scale)
df.groupBy("category_name").count().orderBy("count", ascending=False)
```

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async DB connection string | SQLite |
| `GEMINI_API_KEY` | Google AI Studio API key | — |
| `SECRET_KEY` | JWT signing key (min 32 chars) | dev key |
| `CORS_ORIGINS` | Allowed frontend origins | localhost:5173 |
| `ENVIRONMENT` | development / production | development |
| `DEBUG` | Enable SQLAlchemy query logging | true |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | http://localhost:8000 |

---

*Built with Python 3.11, FastAPI, React 18, scikit-learn, spaCy, Google Gemini 
