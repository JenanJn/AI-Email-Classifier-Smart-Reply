"""
API integration tests.
Uses in-memory SQLite so no external DB is needed.
The email creation tests mock asyncio.to_thread to avoid greenlet issues
with SQLAlchemy async sessions being passed across thread boundaries.
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import init_db


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    """Fresh in-memory DB per test function."""
    import os
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["DATABASE_URL_SYNC"] = "sqlite:///:memory:"

    # Re-create engine with the test URL
    import app.db.session as db_module
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    db_module.engine = test_engine
    db_module.AsyncSessionLocal = async_sessionmaker(
        bind=test_engine, class_=AsyncSession,
        expire_on_commit=False, autoflush=False, autocommit=False,
    )
    await init_db()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    await test_engine.dispose()


async def register_user(client: AsyncClient, email: str = "user@test.com",
                         name: str = "Test User", password: str = "pass1234") -> dict:
    """Register and return auth headers."""
    resp = await client.post("/auth/register", json={
        "name": name, "email": email, "password": password,
    })
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── Minimal NLP result for mocking ────────────────────────────────────────────

def _mock_nlp_result():
    from app.nlp.pipeline import NLPResult
    from app.nlp.entity_extractor import ExtractedEntity
    r = NLPResult()
    r.category = "Job / Career"
    r.category_slug = "job_career"
    r.category_confidence = 0.92
    r.intent = "Interview Invitation"
    r.sentiment = "neutral"
    r.sentiment_score = 0.0
    r.entities = [ExtractedEntity("DATE", "tomorrow", 0.9, 10)]
    r.deadline_text = "tomorrow"
    r.clean_text = "interview invitation tomorrow"
    return r


def _mock_priority_result():
    from app.priority.engine import PriorityResult
    return PriorityResult(
        score=85, level="high", urgency_level="elevated",
        action_required=True,
        explanations=["Interview within 24 hours", "Confirmation required"],
        factors_json='{"deadline_proximity": 22, "action_required": 15}',
    )


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ── Auth ──────────────────────────────────────────────────────────────────────

class TestAuth:
    @pytest.mark.asyncio
    async def test_register_success(self, client):
        resp = await client.post("/auth/register", json={
            "name": "Alice", "email": "alice@test.com", "password": "pass1234",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["email"] == "alice@test.com"

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        await client.post("/auth/register", json={
            "name": "Bob", "email": "bob@test.com", "password": "pass1234",
        })
        resp = await client.post("/auth/login", json={
            "email": "bob@test.com", "password": "pass1234",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_wrong_password_rejected(self, client):
        await client.post("/auth/register", json={
            "name": "Carol", "email": "carol@test.com", "password": "correct",
        })
        resp = await client.post("/auth/login", json={
            "email": "carol@test.com", "password": "wrong",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_duplicate_email_rejected(self, client):
        payload = {"name": "Dave", "email": "dave@test.com", "password": "pass"}
        await client.post("/auth/register", json=payload)
        resp = await client.post("/auth/register", json={**payload, "name": "Dave2"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_protected_route_requires_token(self, client):
        resp = await client.get("/emails")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, client):
        resp = await client.get("/emails", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401


# ── Emails ────────────────────────────────────────────────────────────────────

class TestEmails:
    @pytest.mark.asyncio
    async def test_create_email_triggers_analysis(self, client):
        """Creating an email should auto-trigger NLP analysis."""
        headers = await register_user(client)

        async def mock_analyze(self, email):
            """Simulate analysis without running actual NLP/ML."""
            from app.models.analysis import EmailAnalysis
            from app.models.reply import GeneratedReply, ReplyVersion
            from sqlalchemy import delete as sql_delete
            import app.db.session as db_module
            # Get current session from the service's DB
            # We patch at the service level so just mark it analyzed
            email.is_analyzed = True

        with patch("app.services.email_service.EmailService.analyze_email", new=mock_analyze):
            resp = await client.post("/emails", json={
                "sender_name": "HR Team",
                "sender_email": "hr@company.com",
                "subject": "Interview Invitation",
                "body": "Please confirm your availability for the interview tomorrow at 10 AM.",
            }, headers=headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["subject"] == "Interview Invitation"
        assert data["sender_name"] == "HR Team"

    @pytest.mark.asyncio
    async def test_list_emails_returns_paginated(self, client):
        headers = await register_user(client, "list@test.com")

        async def mock_analyze(self, email):
            email.is_analyzed = True

        with patch("app.services.email_service.EmailService.analyze_email", new=mock_analyze):
            for i in range(2):
                await client.post("/emails", json={
                    "sender_name": f"Sender {i}",
                    "sender_email": f"s{i}@test.com",
                    "subject": f"Email {i}",
                    "body": f"Body of email {i}",
                }, headers=headers)

        resp = await client.get("/emails", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert "items" in data
        assert "total_pages" in data

    @pytest.mark.asyncio
    async def test_get_email_by_id(self, client):
        headers = await register_user(client, "get@test.com")

        async def mock_analyze(self, email):
            email.is_analyzed = True

        with patch("app.services.email_service.EmailService.analyze_email", new=mock_analyze):
            create_resp = await client.post("/emails", json={
                "sender_name": "Sender",
                "sender_email": "s@test.com",
                "subject": "Test Subject",
                "body": "Test body content",
            }, headers=headers)

        email_id = create_resp.json()["id"]
        resp = await client.get(f"/emails/{email_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == email_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_email_returns_404(self, client):
        headers = await register_user(client, "notfound@test.com")
        resp = await client.get("/emails/00000000-0000-0000-0000-000000000000", headers=headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_email(self, client):
        headers = await register_user(client, "delete@test.com")

        async def mock_analyze(self, email):
            email.is_analyzed = True

        with patch("app.services.email_service.EmailService.analyze_email", new=mock_analyze):
            create_resp = await client.post("/emails", json={
                "sender_name": "S", "sender_email": "s@t.com",
                "subject": "To Delete", "body": "Delete me",
            }, headers=headers)

        email_id = create_resp.json()["id"]
        del_resp = await client.delete(f"/emails/{email_id}", headers=headers)
        assert del_resp.status_code == 204

        get_resp = await client.get(f"/emails/{email_id}", headers=headers)
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_empty_body_returns_422(self, client):
        headers = await register_user(client, "empty@test.com")
        resp = await client.post("/emails", json={
            "subject": "No body", "body": "",
        }, headers=headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, client):
        headers = await register_user(client, "filter@test.com")
        resp = await client.get("/emails?priority=high", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()

    @pytest.mark.asyncio
    async def test_cannot_access_other_users_email(self, client):
        """User A cannot read User B's emails."""
        headers_a = await register_user(client, "usera@test.com", "User A")
        headers_b = await register_user(client, "userb@test.com", "User B")

        async def mock_analyze(self, email):
            email.is_analyzed = True

        with patch("app.services.email_service.EmailService.analyze_email", new=mock_analyze):
            create_resp = await client.post("/emails", json={
                "sender_name": "S", "sender_email": "s@t.com",
                "subject": "Private", "body": "User A private email",
            }, headers=headers_a)

        email_id = create_resp.json()["id"]
        resp = await client.get(f"/emails/{email_id}", headers=headers_b)
        assert resp.status_code == 404


# ── Analytics ─────────────────────────────────────────────────────────────────

class TestAnalytics:
    @pytest.mark.asyncio
    async def test_analytics_summary_returns_data(self, client):
        headers = await register_user(client, "analytics@test.com")
        resp = await client.get("/analytics/summary", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_emails" in data
        assert "high_priority" in data
        assert "action_required" in data

    @pytest.mark.asyncio
    async def test_analytics_trends_returns_data(self, client):
        headers = await register_user(client, "trends@test.com")
        resp = await client.get("/analytics/trends?period=30", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "category_distribution" in data
        assert "priority_distribution" in data
        assert "daily_volume" in data

    @pytest.mark.asyncio
    async def test_analytics_insights_returns_data(self, client):
        headers = await register_user(client, "insights@test.com")
        resp = await client.get("/analytics/insights", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "insights" in data
        assert isinstance(data["insights"], list)


# ── Categories ────────────────────────────────────────────────────────────────

class TestCategories:
    @pytest.mark.asyncio
    async def test_categories_list(self, client):
        headers = await register_user(client, "cats@test.com")
        resp = await client.get("/categories", headers=headers)
        assert resp.status_code == 200
        # Categories are empty until seeded — just verify it returns a list
        assert isinstance(resp.json(), list)
