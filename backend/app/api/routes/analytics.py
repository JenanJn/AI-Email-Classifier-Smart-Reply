"""Analytics endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsInsights, AnalyticsSummary, AnalyticsTrends
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_summary(current_user.id)


@router.get("/trends", response_model=AnalyticsTrends)
async def analytics_trends(
    period: int = Query(30, ge=7, le=365, description="Number of days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_trends(current_user.id, period)


@router.get("/insights", response_model=AnalyticsInsights)
async def analytics_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_insights(current_user.id)
