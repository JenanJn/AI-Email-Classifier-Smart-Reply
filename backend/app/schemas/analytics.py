"""Pydantic schemas for Analytics endpoints."""
from typing import Optional

from pydantic import BaseModel


class CategoryCount(BaseModel):
    category: str
    count: int
    percentage: float


class PriorityCount(BaseModel):
    level: str
    count: int
    percentage: float


class DailyVolume(BaseModel):
    date: str
    count: int


class CategoryPriorityAvg(BaseModel):
    category: str
    avg_priority: float


class AnalyticsSummary(BaseModel):
    total_emails: int
    high_priority: int
    medium_priority: int
    low_priority: int
    action_required: int
    analyzed: int
    replies_generated: int
    avg_priority_score: float
    action_required_percentage: float


class AnalyticsTrends(BaseModel):
    daily_volume: list[DailyVolume]
    category_distribution: list[CategoryCount]
    priority_distribution: list[PriorityCount]
    avg_priority_by_category: list[CategoryPriorityAvg]


class AIInsight(BaseModel):
    insight: str
    type: str  # info / warning / tip


class AnalyticsInsights(BaseModel):
    insights: list[AIInsight]
