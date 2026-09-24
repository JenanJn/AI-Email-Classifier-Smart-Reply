"""Email CRUD and analysis endpoints."""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.analysis import EmailAnalysis
from app.models.email import Email
from app.models.user import User
from app.schemas.email import (
    EmailCreate,
    EmailListItem,
    EmailOut,
    EmailUpdate,
    PaginatedEmails,
)
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=EmailOut, status_code=status.HTTP_201_CREATED)
async def create_email(
    payload: EmailCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new email and immediately trigger AI analysis."""
    service = EmailService(db)
    email, _snapshot = await service.create_and_analyze(payload, current_user.id)
    # Reload with relationships
    result = await db.execute(
        select(Email)
        .options(
            selectinload(Email.analysis),
            selectinload(Email.entities),
            selectinload(Email.reply),
        )
        .where(Email.id == email.id)
    )
    email = result.scalar_one()
    return _email_to_out(email)


@router.get("", response_model=PaginatedEmails)
async def list_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    action_required: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List emails with pagination and filters."""
    query = (
        select(Email)
        .options(selectinload(Email.analysis))
        .where(Email.user_id == current_user.id)
        .order_by(Email.received_at.desc())
    )

    # Join analysis for filtering
    if category or priority or action_required is not None:
        query = query.join(EmailAnalysis, Email.id == EmailAnalysis.email_id, isouter=True)
        if category:
            query = query.where(EmailAnalysis.category_name.ilike(f"%{category}%"))
        if priority:
            query = query.where(EmailAnalysis.priority_level == priority.lower())
        if action_required is not None:
            query = query.where(EmailAnalysis.action_required == action_required)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            Email.subject.ilike(search_term)
            | Email.body.ilike(search_term)
            | Email.sender_name.ilike(search_term)
            | Email.sender_email.ilike(search_term)
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    emails = result.scalars().all()

    items = [_email_to_list_item(e) for e in emails]
    return PaginatedEmails(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/{email_id}", response_model=EmailOut)
async def get_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    email = await _get_email_or_404(email_id, current_user.id, db)
    return _email_to_out(email)


@router.post("/{email_id}/analyze", response_model=EmailOut)
async def analyze_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-trigger full AI analysis on an existing email."""
    result = await db.execute(
        select(Email).where(Email.id == email_id, Email.user_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    service = EmailService(db)
    await service.analyze_email(email)

    result = await db.execute(
        select(Email)
        .options(
            selectinload(Email.analysis),
            selectinload(Email.entities),
            selectinload(Email.reply),
        )
        .where(Email.id == email_id)
    )
    email = result.scalar_one()
    return _email_to_out(email)


@router.patch("/{email_id}", response_model=EmailOut)
async def update_email(
    email_id: str,
    payload: EmailUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    email = await _get_email_or_404(email_id, current_user.id, db)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(email, field, value)
    await db.flush()
    await db.refresh(email)
    return _email_to_out(email)


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    email = await _get_email_or_404(email_id, current_user.id, db, load_relations=False)
    await db.delete(email)


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _get_email_or_404(
    email_id: str, user_id: str, db: AsyncSession, load_relations: bool = True
) -> Email:
    q = select(Email).where(Email.id == email_id, Email.user_id == user_id)
    if load_relations:
        q = q.options(
            selectinload(Email.analysis),
            selectinload(Email.entities),
            selectinload(Email.reply),
        )
    result = await db.execute(q)
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


def _email_to_out(email: Email) -> EmailOut:
    analysis = None
    if email.analysis:
        a = email.analysis
        analysis = {
            "id": a.id,
            "category_name": a.category_name,
            "category_confidence": a.category_confidence,
            "intent": a.intent,
            "priority_level": a.priority_level,
            "priority_score": a.priority_score,
            "urgency_level": a.urgency_level,
            "sentiment": a.sentiment,
            "sentiment_score": a.sentiment_score,
            "action_required": a.action_required,
            "deadline_text": a.deadline_text,
            "key_points": a.key_points_list,
            "ai_explanation": a.ai_explanation_list,
            "priority_factors": a.priority_factors,
            "analyzed_at": a.analyzed_at,
        }

    entities = None
    if email.entities:
        entities = [
            {"id": e.id, "entity_type": e.entity_type, "entity_text": e.entity_text, "confidence": e.confidence}
            for e in email.entities
        ]

    reply = None
    if email.reply:
        r = email.reply
        reply = {
            "id": r.id,
            "current_content": r.current_content,
            "tone": r.tone,
            "status": r.status,
            "is_user_edited": r.is_user_edited,
            "generated_at": r.generated_at,
            "updated_at": r.updated_at,
        }

    return EmailOut(
        id=email.id,
        sender_name=email.sender_name,
        sender_email=email.sender_email,
        subject=email.subject,
        body=email.body,
        received_at=email.received_at,
        is_analyzed=email.is_analyzed,
        created_at=email.created_at,
        analysis=analysis,
        entities=entities,
        reply=reply,
    )


def _email_to_list_item(email: Email) -> EmailListItem:
    analysis = email.analysis
    return EmailListItem(
        id=email.id,
        sender_name=email.sender_name,
        sender_email=email.sender_email,
        subject=email.subject,
        received_at=email.received_at,
        is_analyzed=email.is_analyzed,
        category_name=analysis.category_name if analysis else None,
        priority_level=analysis.priority_level if analysis else None,
        priority_score=analysis.priority_score if analysis else None,
        action_required=analysis.action_required if analysis else None,
        intent=analysis.intent if analysis else None,
    )
