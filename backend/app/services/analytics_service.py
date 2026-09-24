"""
Analytics service — aggregates email data for dashboard insights.

Designed to be extensible: all queries use SQLAlchemy so they can
be replaced with Spark/BigQuery queries as data scales.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import EmailAnalysis
from app.models.email import Email
from app.models.reply import GeneratedReply
from app.schemas.analytics import (
    AIInsight,
    AnalyticsInsights,
    AnalyticsSummary,
    AnalyticsTrends,
    CategoryCount,
    CategoryPriorityAvg,
    DailyVolume,
    PriorityCount,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self, user_id: str) -> AnalyticsSummary:
        """Aggregate summary statistics for the user's inbox."""
        # Total emails
        total_result = await self.db.execute(
            select(func.count(Email.id)).where(Email.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # Analyzed count
        analyzed_result = await self.db.execute(
            select(func.count(Email.id)).where(Email.user_id == user_id, Email.is_analyzed == True)
        )
        analyzed = analyzed_result.scalar() or 0

        # Priority breakdown (join with analysis)
        prio_result = await self.db.execute(
            select(
                EmailAnalysis.priority_level,
                func.count(EmailAnalysis.id).label("cnt"),
            )
            .join(Email, Email.id == EmailAnalysis.email_id)
            .where(Email.user_id == user_id)
            .group_by(EmailAnalysis.priority_level)
        )
        priority_counts = {row.priority_level: row.cnt for row in prio_result}

        # Action required
        action_result = await self.db.execute(
            select(func.count(EmailAnalysis.id))
            .join(Email, Email.id == EmailAnalysis.email_id)
            .where(Email.user_id == user_id, EmailAnalysis.action_required == True)
        )
        action_required = action_result.scalar() or 0

        # Average priority score
        avg_result = await self.db.execute(
            select(func.avg(EmailAnalysis.priority_score))
            .join(Email, Email.id == EmailAnalysis.email_id)
            .where(Email.user_id == user_id)
        )
        avg_priority = float(avg_result.scalar() or 0.0)

        # Replies generated
        replies_result = await self.db.execute(
            select(func.count(GeneratedReply.id))
            .join(Email, Email.id == GeneratedReply.email_id)
            .where(Email.user_id == user_id)
        )
        replies_generated = replies_result.scalar() or 0

        action_pct = round((action_required / analyzed * 100) if analyzed > 0 else 0.0, 1)

        return AnalyticsSummary(
            total_emails=total,
            high_priority=priority_counts.get("high", 0),
            medium_priority=priority_counts.get("medium", 0),
            low_priority=priority_counts.get("low", 0),
            action_required=action_required,
            analyzed=analyzed,
            replies_generated=replies_generated,
            avg_priority_score=round(avg_priority, 1),
            action_required_percentage=action_pct,
        )

    async def get_trends(self, user_id: str, period: int = 30) -> AnalyticsTrends:
        """Get trend data for charts."""
        since = datetime.now(timezone.utc) - timedelta(days=period)

        # ── Daily volume ─────────────────────────────────────────────────
        # SQLite-compatible date extraction
        daily_result = await self.db.execute(
            select(
                func.strftime("%Y-%m-%d", Email.received_at).label("date"),
                func.count(Email.id).label("cnt"),
            )
            .where(Email.user_id == user_id, Email.received_at >= since)
            .group_by(func.strftime("%Y-%m-%d", Email.received_at))
            .order_by("date")
        )
        daily_volume = [DailyVolume(date=row.date, count=row.cnt) for row in daily_result]

        # ── Category distribution ────────────────────────────────────────
        cat_result = await self.db.execute(
            select(
                EmailAnalysis.category_name,
                func.count(EmailAnalysis.id).label("cnt"),
            )
            .join(Email, Email.id == EmailAnalysis.email_id)
            .where(Email.user_id == user_id)
            .group_by(EmailAnalysis.category_name)
            .order_by(func.count(EmailAnalysis.id).desc())
        )
        cat_rows = cat_result.all()
        total_analyzed = sum(r.cnt for r in cat_rows) or 1
        category_distribution = [
            CategoryCount(
                category=r.category_name or "Other",
                count=r.cnt,
                percentage=round(r.cnt / total_analyzed * 100, 1),
            )
            for r in cat_rows
        ]

        # ── Priority distribution ────────────────────────────────────────
        prio_result = await self.db.execute(
            select(
                EmailAnalysis.priority_level,
                func.count(EmailAnalysis.id).label("cnt"),
            )
            .join(Email, Email.id == EmailAnalysis.email_id)
            .where(Email.user_id == user_id)
            .group_by(EmailAnalysis.priority_level)
        )
        prio_rows = prio_result.all()
        total_prio = sum(r.cnt for r in prio_rows) or 1
        priority_distribution = [
            PriorityCount(
                level=r.priority_level or "unknown",
                count=r.cnt,
                percentage=round(r.cnt / total_prio * 100, 1),
            )
            for r in prio_rows
        ]

        # ── Average priority by category ─────────────────────────────────
        avg_result = await self.db.execute(
            select(
                EmailAnalysis.category_name,
                func.avg(EmailAnalysis.priority_score).label("avg_score"),
            )
            .join(Email, Email.id == EmailAnalysis.email_id)
            .where(Email.user_id == user_id)
            .group_by(EmailAnalysis.category_name)
            .order_by(func.avg(EmailAnalysis.priority_score).desc())
        )
        avg_by_cat = [
            CategoryPriorityAvg(
                category=row.category_name or "Other",
                avg_priority=round(float(row.avg_score or 0), 1),
            )
            for row in avg_result
        ]

        return AnalyticsTrends(
            daily_volume=daily_volume,
            category_distribution=category_distribution,
            priority_distribution=priority_distribution,
            avg_priority_by_category=avg_by_cat,
        )

    async def get_insights(self, user_id: str) -> AnalyticsInsights:
        """Generate AI-style textual insights from email analytics."""
        summary = await self.get_summary(user_id)
        trends = await self.get_trends(user_id, 30)
        insights: list[AIInsight] = []

        if summary.total_emails == 0:
            return AnalyticsInsights(insights=[
                AIInsight(
                    insight="No emails analyzed yet. Add emails to see insights.",
                    type="info",
                )
            ])

        # Action required insight
        if summary.action_required > 0:
            insights.append(AIInsight(
                insight=f"{summary.action_required} email{'s' if summary.action_required > 1 else ''} currently require your response.",
                type="warning",
            ))

        # High priority insight
        if summary.high_priority > 0:
            insights.append(AIInsight(
                insight=f"{summary.high_priority} high-priority email{'s are' if summary.high_priority > 1 else ' is'} in your inbox.",
                type="warning",
            ))

        # Most common category
        if trends.category_distribution:
            top_cat = trends.category_distribution[0]
            insights.append(AIInsight(
                insight=f"'{top_cat.category}' is your most frequent email category ({top_cat.percentage}% of inbox).",
                type="info",
            ))

        # Highest avg priority category
        if trends.avg_priority_by_category:
            top = trends.avg_priority_by_category[0]
            insights.append(AIInsight(
                insight=f"'{top.category}' emails have the highest average priority score ({top.avg_priority}/100).",
                type="info",
            ))

        # Average priority
        if summary.avg_priority_score > 65:
            insights.append(AIInsight(
                insight=f"Your inbox average priority is {summary.avg_priority_score}/100 — above normal.",
                type="warning",
            ))
        elif summary.avg_priority_score < 35:
            insights.append(AIInsight(
                insight=f"Your inbox average priority is {summary.avg_priority_score}/100 — mostly low-priority content.",
                type="info",
            ))

        # Reply rate
        if summary.analyzed > 0:
            reply_rate = round(summary.replies_generated / summary.analyzed * 100)
            insights.append(AIInsight(
                insight=f"AI has generated replies for {reply_rate}% of your analyzed emails.",
                type="info",
            ))

        return AnalyticsInsights(insights=insights)
