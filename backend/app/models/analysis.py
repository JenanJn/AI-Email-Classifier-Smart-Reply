"""EmailAnalysis model — stores all AI/NLP analysis results for an email."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmailAnalysis(Base):
    __tablename__ = "email_analysis"

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
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    category_name: Mapped[str] = mapped_column(String(100), nullable=True)
    category_confidence: Mapped[float] = mapped_column(Float, nullable=True)  # 0.0–1.0

    intent: Mapped[str] = mapped_column(String(255), nullable=True)

    priority_level: Mapped[str] = mapped_column(String(20), nullable=True)  # low/medium/high
    priority_score: Mapped[int] = mapped_column(Integer, nullable=True)     # 0–100
    urgency_level: Mapped[str] = mapped_column(String(20), nullable=True)

    sentiment: Mapped[str] = mapped_column(String(50), nullable=True)       # positive/neutral/negative
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)    # -1.0 to 1.0

    action_required: Mapped[bool] = mapped_column(Boolean, default=False)
    deadline_text: Mapped[str] = mapped_column(String(255), nullable=True)
    deadline_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Stored as pipe-separated strings (SQLite-compatible; use ARRAY for PostgreSQL)
    key_points: Mapped[str] = mapped_column(Text, nullable=True)       # "point1|||point2"
    ai_explanation: Mapped[str] = mapped_column(Text, nullable=True)   # "reason1|||reason2"
    priority_factors: Mapped[str] = mapped_column(Text, nullable=True) # JSON string

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    email: Mapped["Email"] = relationship("Email", back_populates="analysis")  # noqa: F821
    category: Mapped["Category"] = relationship("Category", back_populates="analyses")  # noqa: F821

    # Helpers to convert pipe-separated to list
    @property
    def key_points_list(self) -> list[str]:
        if not self.key_points:
            return []
        return [p for p in self.key_points.split("|||") if p.strip()]

    @property
    def ai_explanation_list(self) -> list[str]:
        if not self.ai_explanation:
            return []
        return [e for e in self.ai_explanation.split("|||") if e.strip()]
