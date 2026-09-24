"""
Seed the database with:
1. Categories
2. A demo user
3. Sample emails (with full AI analysis)

Run: python -m scripts.seed_db  (from the backend/ directory)
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal, init_db
from app.ml.classifier import CATEGORIES
from app.models.category import Category
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.schemas.email import EmailCreate
from app.services.email_service import EmailService

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

# Force absolute path for the DB so it works regardless of working directory
_db_path = Path(__file__).parent.parent / "email_classifier.db"
os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{_db_path.as_posix()}"
)
os.environ.setdefault(
    "DATABASE_URL_SYNC",
    f"sqlite:///{_db_path.as_posix()}"
)

DEMO_USER = {
    "name": "Demo User",
    "email": "demo@emailai.com",
    "password": "demo1234",
}


async def seed_categories() -> None:
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Category))
        existing = {c.slug for c in result.scalars().all()}
        added = 0
        for cat in CATEGORIES:
            if cat["slug"] not in existing:
                db.add(Category(
                    name=cat["name"],
                    slug=cat["slug"],
                    icon=cat["icon"],
                    color=cat["color"],
                ))
                added += 1
        await db.commit()
    logger.info("Categories: %d added, %d already existed", added, len(existing))


async def seed_user() -> User:
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == DEMO_USER["email"]))
        user = result.scalar_one_or_none()
        if user:
            if not verify_password(DEMO_USER["password"], user.hashed_password):
                logger.warning("Demo user password hash was invalid or stale; rehashing it.")
                user.hashed_password = hash_password(DEMO_USER["password"])
                await db.commit()
            logger.info("Demo user already exists: %s", user.email)
            return user
        user = User(
            name=DEMO_USER["name"],
            email=DEMO_USER["email"],
            hashed_password=hash_password(DEMO_USER["password"]),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    logger.info("Demo user created: %s", user.email)
    return user


async def seed_single_email(item: dict, user_id: str, received_at: datetime, idx: int, total: int) -> bool:
    """Each email gets its own session to avoid greenlet / expiry issues."""
    async with AsyncSessionLocal() as db:
        payload = EmailCreate(
            sender_name=item["sender_name"],
            sender_email=item["sender_email"],
            subject=item["subject"],
            body=item["body"],
            received_at=received_at,
        )
        try:
            service = EmailService(db)
            email, snapshot = await service.create_and_analyze(payload, user_id)
            # Read plain values from snapshot — no ORM lazy-load
            cat = snapshot.category_name
            pri = snapshot.priority_score
            await db.commit()
            logger.info("[%d/%d] OK '%s'  ->  %s  (priority: %s)",
                        idx + 1, total, item["subject"][:50], cat, pri)
            return True
        except Exception as e:
            await db.rollback()
            logger.error(
                "[%d/%d] FAIL '%s': %s",
                idx + 1, total,
                item["subject"][:40], e,
            )
            return False


async def seed_emails(user_id: str) -> None:
    data_path = Path(__file__).parent.parent / "data" / "seed_emails.json"
    with open(data_path, encoding="utf-8") as f:
        seed_data = json.load(f)

    total = len(seed_data)
    success = 0
    for i, item in enumerate(seed_data):
        days_ago = item.get("days_ago", i)
        received_at = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=i % 8)
        ok = await seed_single_email(item, user_id, received_at, i, total)
        if ok:
            success += 1

    logger.info("Emails seeded: %d/%d succeeded", success, total)


async def main():
    logger.info("Initializing database…")
    await init_db()

    await seed_categories()
    user = await seed_user()
    await seed_emails(user.id)

    logger.info("\n✓ Seeding complete!")
    logger.info("  Demo login: %s / %s", DEMO_USER["email"], DEMO_USER["password"])


if __name__ == "__main__":
    asyncio.run(main())
