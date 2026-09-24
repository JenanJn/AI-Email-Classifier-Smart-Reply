"""Reply generation and management endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.email import Email
from app.models.reply import GeneratedReply, ReplyVersion
from app.models.user import User
from app.schemas.reply import ReplyEditRequest, ReplyModifyRequest, ReplyOut, ReplyVersionOut
from app.services.reply_service import ReplyService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{email_id}/reply/generate", response_model=ReplyOut)
async def generate_reply(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate the initial AI reply for an email."""
    email = await _get_email_or_404(email_id, current_user.id, db)
    service = ReplyService(db)
    reply = await service.generate(email)
    return _reply_to_out(reply)


@router.post("/{email_id}/reply/regenerate", response_model=ReplyOut)
async def regenerate_reply(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new variation of the reply."""
    email = await _get_email_or_404(email_id, current_user.id, db)
    service = ReplyService(db)
    reply = await service.regenerate(email)
    return _reply_to_out(reply)


@router.post("/{email_id}/reply/modify", response_model=ReplyOut)
async def modify_reply(
    email_id: str,
    payload: ReplyModifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Modify the reply style: shorter / formal / friendly / longer."""
    email = await _get_email_or_404(email_id, current_user.id, db)
    service = ReplyService(db)
    reply = await service.modify(email, payload.style)
    return _reply_to_out(reply)


@router.patch("/{email_id}/reply", response_model=ReplyOut)
async def edit_reply(
    email_id: str,
    payload: ReplyEditRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save user-edited reply content."""
    email = await _get_email_or_404(email_id, current_user.id, db)
    if not email.reply:
        raise HTTPException(status_code=404, detail="No reply generated yet")

    service = ReplyService(db)
    reply = await service.save_edit(email.reply, payload)
    return _reply_to_out(reply)


@router.get("/{email_id}/reply/history", response_model=list[ReplyVersionOut])
async def reply_history(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all versions of the reply."""
    email = await _get_email_or_404(email_id, current_user.id, db)
    if not email.reply:
        return []

    result = await db.execute(
        select(ReplyVersion)
        .where(ReplyVersion.reply_id == email.reply.id)
        .order_by(ReplyVersion.version_num)
    )
    versions = result.scalars().all()
    return [ReplyVersionOut.model_validate(v) for v in versions]


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_email_or_404(email_id: str, user_id: str, db: AsyncSession) -> Email:
    result = await db.execute(
        select(Email)
        .options(
            selectinload(Email.analysis),
            selectinload(Email.reply).selectinload(GeneratedReply.versions),
        )
        .where(Email.id == email_id, Email.user_id == user_id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


def _reply_to_out(reply: GeneratedReply) -> ReplyOut:
    versions = [
        ReplyVersionOut(
            id=v.id,
            version_num=v.version_num,
            content=v.content,
            change_type=v.change_type,
            created_at=v.created_at,
        )
        for v in (reply.versions or [])
    ]
    return ReplyOut(
        id=reply.id,
        email_id=reply.email_id,
        current_content=reply.current_content,
        tone=reply.tone,
        status=reply.status,
        is_user_edited=reply.is_user_edited,
        generated_at=reply.generated_at,
        updated_at=reply.updated_at,
        versions=versions,
    )
