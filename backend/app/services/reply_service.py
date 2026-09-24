"""Reply service — manages reply generation, modification, and editing."""
import logging
from typing import Optional

from sqlalchemy import delete as sql_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reply import GeneratedReply, ReplyVersion
from app.models.email import Email
from app.schemas.reply import ReplyEditRequest

logger = logging.getLogger(__name__)


class ReplyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(self, email: Email) -> GeneratedReply:
        """Generate initial reply for an email (or replace existing)."""
        from app.genai.reply_generator import generate_reply

        if not email.analysis:
            raise ValueError("Email must be analyzed before generating a reply")

        entities = [
            {"entity_type": e.entity_type, "entity_text": e.entity_text}
            for e in (email.entities or [])
        ]
        slug = self._slug_from_name(email.analysis.category_name)

        reply_text = generate_reply(
            email.subject or "",
            email.body or "",
            email.sender_name,
            email.analysis.category_name or "Other",
            slug,
            email.analysis.intent or "General Information",
            email.analysis.action_required,
            email.analysis.deadline_text,
            entities,
        )

        return await self._save_version(email, reply_text, "generated")

    async def regenerate(self, email: Email) -> GeneratedReply:
        """Generate a new variation."""
        from app.genai.reply_generator import generate_reply

        if not email.analysis:
            raise ValueError("Email not analyzed")

        entities = [
            {"entity_type": e.entity_type, "entity_text": e.entity_text}
            for e in (email.entities or [])
        ]
        slug = self._slug_from_name(email.analysis.category_name)

        reply_text = generate_reply(
            email.subject or "",
            email.body or "",
            email.sender_name,
            email.analysis.category_name or "Other",
            slug,
            email.analysis.intent or "General Information",
            email.analysis.action_required,
            email.analysis.deadline_text,
            entities,
        )

        return await self._save_version(email, reply_text, "regenerated")

    async def modify(self, email: Email, style: str) -> GeneratedReply:
        """Modify reply style: shorter / formal / friendly / longer."""
        from app.genai.reply_generator import modify_reply

        reply = email.reply
        if not reply:
            return await self.generate(email)

        slug = self._slug_from_name(email.analysis.category_name if email.analysis else "other")
        modified = modify_reply(reply.current_content, style, slug)

        return await self._save_version(email, modified, style)

    async def save_edit(self, reply: GeneratedReply, payload: ReplyEditRequest) -> GeneratedReply:
        """Save user-edited reply content."""
        result = await self.db.execute(
            select(ReplyVersion).where(ReplyVersion.reply_id == reply.id)
        )
        versions = result.scalars().all()
        next_version = len(versions) + 1

        reply.current_content = payload.content
        reply.is_user_edited = True
        if payload.status:
            reply.status = payload.status

        self.db.add(ReplyVersion(
            reply_id=reply.id,
            content=payload.content,
            version_num=next_version,
            change_type="user_edit",
        ))
        await self.db.flush()
        await self.db.refresh(reply)
        return reply

    async def _save_version(self, email: Email, text: str, change_type: str) -> GeneratedReply:
        """Create or update the GeneratedReply and append a ReplyVersion."""
        reply = email.reply

        if reply is None:
            reply = GeneratedReply(
                email_id=email.id,
                current_content=text,
                tone="formal",
                status="draft",
            )
            self.db.add(reply)
            await self.db.flush()
            version_num = 1
        else:
            # Count existing versions
            result = await self.db.execute(
                select(ReplyVersion).where(ReplyVersion.reply_id == reply.id)
            )
            version_num = len(result.scalars().all()) + 1
            reply.current_content = text
            reply.is_user_edited = False

        self.db.add(ReplyVersion(
            reply_id=reply.id,
            content=text,
            version_num=version_num,
            change_type=change_type,
        ))
        await self.db.flush()
        await self.db.refresh(reply)
        return reply

    @staticmethod
    def _slug_from_name(name: Optional[str]) -> str:
        if not name:
            return "other"
        return name.lower().replace(" / ", "_").replace(" ", "_").replace("-", "_")
