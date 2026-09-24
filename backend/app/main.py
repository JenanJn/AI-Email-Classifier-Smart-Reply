"""
AI Email Classifier — FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.session import init_db
from app.api.routes import emails, analytics, categories, replies, health, auth

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, clean up on shutdown."""
    logger.info("Starting AI Email Classifier API...")
    await init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered email classification, priority scoring, "
        "entity extraction, and smart reply generation."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["System"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(emails.router, prefix="/emails", tags=["Emails"])
app.include_router(replies.router, prefix="/emails", tags=["Replies"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
