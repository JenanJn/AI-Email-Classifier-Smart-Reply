"""Pydantic schemas for Email endpoints."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class EmailCreate(BaseModel):
    sender_name: Optional[str] = Field(None, max_length=255)
    sender_email: Optional[str] = Field(None, max_length=255)
    subject: Optional[str] = None
    body: str = Field(..., min_length=1)
    received_at: Optional[datetime] = None


class EmailUpdate(BaseModel):
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    received_at: Optional[datetime] = None


class EntityOut(BaseModel):
    id: str
    entity_type: str
    entity_text: str
    confidence: Optional[float] = None

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    id: str
    category_name: Optional[str] = None
    category_confidence: Optional[float] = None
    intent: Optional[str] = None
    priority_level: Optional[str] = None
    priority_score: Optional[int] = None
    urgency_level: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    action_required: bool = False
    deadline_text: Optional[str] = None
    key_points: Optional[list[str]] = None
    ai_explanation: Optional[list[str]] = None
    priority_factors: Optional[str] = None
    analyzed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReplyOut(BaseModel):
    id: str
    current_content: str
    tone: str
    status: str
    is_user_edited: bool
    generated_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailOut(BaseModel):
    id: str
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    body: str
    received_at: datetime
    is_analyzed: bool
    created_at: datetime
    analysis: Optional[AnalysisOut] = None
    entities: Optional[list[EntityOut]] = None
    reply: Optional[ReplyOut] = None

    model_config = {"from_attributes": True}


class EmailListItem(BaseModel):
    """Lightweight email representation for list views."""
    id: str
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    received_at: datetime
    is_analyzed: bool
    # Analysis fields for list display
    category_name: Optional[str] = None
    priority_level: Optional[str] = None
    priority_score: Optional[int] = None
    action_required: Optional[bool] = None
    intent: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedEmails(BaseModel):
    items: list[EmailListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
