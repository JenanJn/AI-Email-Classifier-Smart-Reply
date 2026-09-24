"""Category model — extensible list of email categories."""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)   # Lucide icon name
    color: Mapped[str] = mapped_column(String(20), nullable=True)  # hex color
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    analyses: Mapped[list["EmailAnalysis"]] = relationship(  # noqa: F821
        "EmailAnalysis", back_populates="category"
    )
