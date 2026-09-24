"""GeneratedReply and ReplyVersion models."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GeneratedReply(Base):
    __tablename__ = "generated_replies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("emails.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    current_content: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(String(50), default="formal")  # formal/friendly/concise
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/sent/discarded
    is_user_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    email: Mapped["Email"] = relationship("Email", back_populates="reply")  # noqa: F821
    versions: Mapped[list["ReplyVersion"]] = relationship(
        "ReplyVersion", back_populates="reply", cascade="all, delete-orphan", order_by="ReplyVersion.version_num"
    )


class ReplyVersion(Base):
    __tablename__ = "reply_versions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    reply_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("generated_replies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version_num: Mapped[int] = mapped_column(Integer, nullable=False)
    # generated / regenerated / shorter / formal / friendly / user_edit
    change_type: Mapped[str] = mapped_column(String(50), default="generated")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    reply: Mapped["GeneratedReply"] = relationship("GeneratedReply", back_populates="versions")
