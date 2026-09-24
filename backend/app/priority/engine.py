"""
Priority scoring engine.

Computes a 0–100 priority score by aggregating weighted signals.
Returns the score, level (low/medium/high), and a list of human-readable
explanations suitable for display in the UI.

Score bands:
  0–39  → Low
  40–69 → Medium
  70–100→ High
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from app.priority.signals import (
    signal_action_required,
    signal_category_base,
    signal_deadline_proximity,
    signal_event_scheduled,
    signal_financial_security,
    signal_sender_importance,
    signal_time_sensitive_language,
    signal_urgency_words,
)

logger = logging.getLogger(__name__)


@dataclass
class PriorityResult:
    score: int
    level: str           # low / medium / high
    urgency_level: str   # normal / elevated / critical
    action_required: bool
    explanations: list[str] = field(default_factory=list)
    factors_json: str = "{}"  # JSON breakdown for transparency


def compute_priority(
    subject: str,
    body: str,
    category_slug: str,
    sender_email: Optional[str] = None,
) -> PriorityResult:
    """
    Compute the priority score for an email.
    All signals are independently calculated then summed.
    """
    combined_text = f"{subject or ''} {body or ''}"
    explanations: list[str] = []
    factors: dict[str, int] = {}

    # ── Run all signals ───────────────────────────────────────────────────

    s1, r1 = signal_urgency_words(combined_text)
    if r1:
        explanations.append(r1)
    factors["urgency_words"] = s1

    s2, r2 = signal_deadline_proximity(combined_text)
    if r2:
        explanations.append(r2)
    factors["deadline_proximity"] = s2

    s3, r3, action_required = signal_action_required(combined_text)
    if r3:
        explanations.append(r3)
    factors["action_required"] = s3

    s4, r4 = signal_category_base(category_slug)
    if r4:
        explanations.append(r4)
    factors["category_importance"] = s4

    s5, r5 = signal_event_scheduled(combined_text)
    if r5:
        explanations.append(r5)
    factors["event_scheduled"] = s5

    s6, r6 = signal_financial_security(combined_text)
    if r6:
        explanations.append(r6)
    factors["security_alert"] = s6

    s7, r7 = signal_time_sensitive_language(combined_text)
    if r7:
        explanations.append(r7)
    factors["time_sensitive"] = s7

    s8, r8 = signal_sender_importance(sender_email)
    if r8:
        explanations.append(r8)
    factors["sender_importance"] = s8

    # ── Aggregate ─────────────────────────────────────────────────────────
    raw_score = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8
    score = min(raw_score, 100)

    # Determine level
    if score >= 70:
        level = "high"
        urgency_level = "critical" if score >= 90 else "elevated"
    elif score >= 40:
        level = "medium"
        urgency_level = "elevated" if score >= 55 else "normal"
    else:
        level = "low"
        urgency_level = "normal"

    # Ensure action_required is always set for high-priority emails
    if score >= 70 and s5 > 0:
        action_required = True

    logger.debug("Priority computed: score=%d level=%s factors=%s", score, level, factors)

    return PriorityResult(
        score=score,
        level=level,
        urgency_level=urgency_level,
        action_required=action_required,
        explanations=explanations,
        factors_json=json.dumps(factors),
    )
