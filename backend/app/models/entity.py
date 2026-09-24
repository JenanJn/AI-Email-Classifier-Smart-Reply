"""EmailEntity model — named entities extracted from email body."""
import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmailEntity(Base):
    __tablename__ = "email_entities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # PERSON, ORG, DATE, TIME, MONEY, GPE, EVENT
    entity_text: Mapped[str] = mapped_column(String(500), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    char_position: Mapped[int] = mapped_column(Integer, nullable=True)

    # Relationships
    email: Mapped["Email"] = relationship("Email", back_populates="entities")  # noqa: F821
