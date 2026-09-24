"""Email model — stores raw email data."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_name: Mapped[str] = mapped_column(String(255), nullable=True)
    sender_email: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    subject: Mapped[str] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="emails")  # noqa: F821
    analysis: Mapped["EmailAnalysis"] = relationship(  # noqa: F821
        "EmailAnalysis", back_populates="email", uselist=False, cascade="all, delete-orphan"
    )
    entities: Mapped[list["EmailEntity"]] = relationship(  # noqa: F821
        "EmailEntity", back_populates="email", cascade="all, delete-orphan"
    )
    reply: Mapped["GeneratedReply"] = relationship(  # noqa: F821
        "GeneratedReply", back_populates="email", uselist=False, cascade="all, delete-orphan"
    )
