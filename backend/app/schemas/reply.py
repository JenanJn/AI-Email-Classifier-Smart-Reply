"""Pydantic schemas for Reply endpoints."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class ReplyModifyRequest(BaseModel):
    style: Literal["shorter", "formal", "friendly", "longer"]


class ReplyEditRequest(BaseModel):
    content: str
    status: Optional[Literal["draft", "sent", "discarded"]] = None


class ReplyVersionOut(BaseModel):
    id: str
    version_num: int
    content: str
    change_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplyOut(BaseModel):
    id: str
    email_id: str
    current_content: str
    tone: str
    status: str
    is_user_edited: bool
    generated_at: datetime
    updated_at: datetime
    versions: Optional[list[ReplyVersionOut]] = None

    model_config = {"from_attributes": True}
